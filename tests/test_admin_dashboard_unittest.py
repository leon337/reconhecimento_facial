"""Testes isolados do dashboard e do histórico do Potiguar."""
from datetime import datetime
import unittest

from main import create_app
from app.models import db, Company, Employee, User, Ponto
from app.biometric_models import BiometricProfile
from app.rbac import AccessRole


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True, "SECRET_KEY": "dashboard-test",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False, "AUTO_CREATE_SCHEMA": True,
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            admin = User(username="admin-demo", name="Admin", role="admin",
                         access_role=AccessRole.SUPER_ADMIN.value)
            admin.set_password("dashboard-test-secret")
            employee = Employee(name="Funcionario E2E de Teste")
            staff = User(username="e2e.teste", name="Funcionario E2E de Teste",
                         employee=employee)
            staff.set_password("dashboard-test-secret")
            other_co = Company(name="Empresa externa", slug="empresa-externa")
            other_emp = Employee(name="OUTSIDE RECORD", company=other_co)
            other_staff = User(username="outside", name="OUTSIDE RECORD",
                               employee=other_emp, company=other_co)
            other_staff.set_password("dashboard-test-secret")
            db.session.add_all([admin, staff, other_staff])
            db.session.flush()
            db.session.add_all([
                Ponto.from_user(staff, tipo="ENTRADA", timestamp=datetime(2026, 11, 12, 2, 58, 13)),
                Ponto.from_user(other_staff, tipo="SAIDA", timestamp=datetime(2026, 11, 12, 3, 2, 13)),
                BiometricProfile(user_id=staff.id, encrypted_template="fixture-not-a-real-face", active=True),
            ])
            db.session.commit()
            self.admin_id = admin.id
            self.other_id = other_staff.id

    def login(self, user_id=None, company_id=None):
        with self.client.session_transaction() as sess:
            sess["admin_user_id"] = user_id or self.admin_id
            sess["admin_company_id"] = company_id
            sess["admin_worksite_id"] = None

    def test_private_routes(self):
        for path in ("/admin/dashboard", "/admin/pontos"):
            r=self.client.get(path)
            self.assertEqual(r.status_code,302)
            self.assertIn("/admin/login",r.location)

    def test_dashboard_scoped_to_current_account(self):
        self.login()
        r=self.client.get("/admin/dashboard")
        self.assertEqual(r.status_code,200)
        body=r.get_data(as_text=True)
        self.assertIn("Dashboard de ponto",body)
        self.assertIn("Funcionario E2E de Teste",body)
        self.assertNotIn("OUTSIDE RECORD",body)
        self.assertIn("11/11/2026 23:58:13",body)
        self.assertIn("Biometrias ativas",body)

    def test_history_filters_and_dates(self):
        self.login()
        url="/admin/pontos"
        r=self.client.get(url)
        self.assertEqual(r.status_code,200)
        self.assertIn("Funcionario E2E de Teste",r.get_data(as_text=True))
        self.assertNotIn("OUTSIDE RECORD",r.get_data(as_text=True))
        self.assertIn("11/11/2026 23:58:13",r.get_data(as_text=True))
        self.assertIn("1 registro(s)",r.get_data(as_text=True))
        self.assertIn("1 registro(s)",self.client.get(url+"?data=2026-11-11").get_data(as_text=True))
        self.assertIn("0 registro(s)",self.client.get(url+"?data=2026-11-12").get_data(as_text=True))
        self.assertIn("0 registro(s)",self.client.get(url+"?tipo=SAIDA").get_data(as_text=True))
        self.assertIn("1 registro(s)",self.client.get(url+"?tipo=ENTRADA").get_data(as_text=True))

    def test_invalid_query_rejected(self):
        self.login()
        for path in ("/admin/pontos?data=no", "/admin/pontos?tipo=INVALIDO", "/admin/pontos?pagina=0", "/admin/pontos?pagina=-1"):
            self.assertEqual(self.client.get(path).status_code,400)

    def test_tenant_scoping(self):
        with self.app.app_context():
            outside=User.query.filter_by(username="outside").one()
            company_id=outside.company_id
            outside_id=outside.id
        self.login(outside_id, company_id)
        body=self.client.get("/admin/pontos").get_data(as_text=True)
        self.assertNotIn("Funcionario E2E de Teste",body)
        # A conta operacional sem permissão USERS_VIEW não acessa o relatório.
        self.assertEqual(self.client.get("/admin/pontos").status_code,403)


if __name__=="__main__":
    unittest.main(verbosity=2)
