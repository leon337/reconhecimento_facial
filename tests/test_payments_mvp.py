"""Fase 01: isolamento de folha, integridade de períodos e jornadas sem pagamento."""
import unittest
from datetime import time, timezone

from main import create_app
from app.models import db, Company, Worksite, Employee, User
from app.payment_models import PaymentPeriod, PaymentWorkEntry
from app.audit_models import AuditEvent
from app.payment_time import calculate_worked_minutes, duration_label
from app.rbac import AccessRole, Permission


class PaymentTimeTests(unittest.TestCase):
    def test_calculation_is_time_only(self):
        self.assertEqual(
            calculate_worked_minutes(time(8), time(12), time(13), time(17)), 480
        )
        self.assertEqual(duration_label(480), "08:00")

    def test_invalid_ranges_rejected(self):
        for times in (
            (time(8), time(7), time(13), time(17)),
            (time(8), time(12), time(11), time(17)),
            (time(18), time(22), time(23), time(3)),
            (time(8, 0, 1), time(12), time(13), time(17)),
            (time(8, tzinfo=timezone.utc), time(12), time(13), time(17)),
        ):
            with self.assertRaises(ValueError):
                calculate_worked_minutes(*times)


class PaymentHttpTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "synthetic-payment-tests",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "AUTO_CREATE_SCHEMA": True,
            "WTF_CSRF_ENABLED": False,
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            a = Company(name="Empresa A Fictícia", slug="empresa-a-ficticia")
            b = Company(name="Empresa B Fictícia", slug="empresa-b-ficticia")
            site_a = Worksite(name="Obra A", company=a)
            site_b = Worksite(name="Obra B", company=a)
            site_foreign = Worksite(name="Obra Externa", company=b)
            employee_a = Employee(name="Trabalhador Fictício A", company=a, worksite=site_a)
            employee_b = Employee(name="Trabalhador Fictício B", company=a, worksite=site_b)
            outsider = Employee(name="DADO EXTERNO", company=b, worksite=site_foreign)
            admin = User(username="finance-admin", company=a, access_role=AccessRole.ADMIN.value)
            manager = User(username="finance-manager", company=a, access_role=AccessRole.MANAGER.value)
            operator = User(username="finance-operator", company=a, access_role=AccessRole.OPERATOR.value)
            auditor = User(username="finance-auditor", company=a, access_role=AccessRole.AUDITOR.value)
            isolated = User(
                username="finance-site-admin", company=a, worksite=site_a,
                access_role=AccessRole.ADMIN.value
            )
            external_admin = User(username="finance-external", company=b, access_role=AccessRole.ADMIN.value)
            legacy = User(username="finance-legacy", access_role=AccessRole.SUPER_ADMIN.value)
            for user in (admin, manager, operator, auditor, isolated, external_admin, legacy):
                user.set_password("synthetic-test-only-password")
            db.session.add_all([
                a, b, site_a, site_b, site_foreign, employee_a, employee_b, outsider,
                admin, manager, operator, auditor, isolated, external_admin, legacy,
            ])
            db.session.commit()
            self.ids = {
                "admin": admin.id, "manager": manager.id, "operator": operator.id,
                "auditor": auditor.id, "isolated": isolated.id, "external": external_admin.id,
                "legacy": legacy.id, "site": site_a.id, "site_b": site_b.id,
                "employee": employee_a.id, "employee_b": employee_b.id,
                "outsider": outsider.id, "company": a.id,
            }

    def login(self, role):
        with self.client.session_transaction() as session:
            session["admin_user_id"] = self.ids[role]

    def period(self, *, site="site", start="2026-08-01", end="2026-08-07"):
        data = {"inicio": start, "fim": end, "obra": str(self.ids[site]) if site else ""}
        return self.client.post("/admin/pagamentos/periodos", data=data)

    def entry(self, period_id, *, employee="employee", day="2026-08-03", **changes):
        data = {
            "funcionario": str(self.ids[employee]), "data": day,
            "entrada": "08:00", "intervalo_inicio": "12:00",
            "intervalo_fim": "13:00", "saida": "17:00",
        }
        data.update(changes)
        return self.client.post(f"/admin/pagamentos/periodos/{period_id}/jornadas", data=data)

    def make_period(self, **kwargs):
        response = self.period(**kwargs)
        self.assertEqual(response.status_code, 303)
        with self.app.app_context():
            return PaymentPeriod.query.order_by(PaymentPeriod.id.desc()).first().id

    def test_requires_auth_roles_and_company(self):
        self.assertEqual(self.client.get("/admin/pagamentos").status_code, 302)
        self.login("operator")
        self.assertEqual(self.client.get("/admin/pagamentos").status_code, 403)
        self.login("legacy")
        self.assertEqual(self.client.get("/admin/pagamentos").status_code, 403)
        self.login("manager")
        self.assertEqual(self.client.get("/admin/pagamentos").status_code, 200)
        self.assertEqual(self.period().status_code, 403)
        self.login("auditor")
        self.assertEqual(self.client.get("/admin/pagamentos").status_code, 200)
        self.assertEqual(self.period().status_code, 403)

    def test_period_and_workday_flow(self):
        self.login("admin")
        pid = self.make_period()
        page = self.client.get(f"/admin/pagamentos/periodos/{pid}")
        self.assertEqual(page.status_code, 200)
        self.assertIn("Trabalhador Fictício A", page.get_data(as_text=True))
        self.assertNotIn("DADO EXTERNO", page.get_data(as_text=True))
        self.assertEqual(self.entry(pid).status_code, 303)
        page = self.client.get(f"/admin/pagamentos/periodos/{pid}")
        self.assertIn("<strong>08:00</strong> horas registradas", page.get_data(as_text=True))
        self.assertIn("no-store", page.headers["Cache-Control"])
        with self.app.app_context():
            period = db.session.get(PaymentPeriod, pid)
            self.assertEqual(period.status, "draft")
            self.assertEqual(len(period.entries), 1)
            self.assertEqual(period.entries[0].worked_minutes, 480)
            self.assertFalse(hasattr(period, "approved_at"))
            self.assertFalse(hasattr(period.entries[0], "amount"))
            self.assertEqual(
                AuditEvent.query.filter(
                    AuditEvent.action.in_(("payments.period.created", "payments.entry.created"))
                ).count(), 2
            )
        self.assertEqual(self.entry(pid).status_code, 409)

    def test_post_requires_csrf_when_enabled(self):
        self.login("admin")
        self.app.config["WTF_CSRF_ENABLED"] = True
        self.assertEqual(self.period().status_code, 400)

    def test_duplicate_or_invalid_periods(self):
        self.login("admin")
        self.make_period()
        self.assertEqual(self.period().status_code, 409)
        self.assertEqual(self.period(start="2026-08-01", end="2026-08-04").status_code, 400)
        self.assertEqual(self.period(start="no-date").status_code, 400)
        self.assertEqual(self.period(site="site_b").status_code, 303)

    def test_out_of_scope_people_and_date_checks(self):
        self.login("admin")
        pid = self.make_period()
        self.assertEqual(self.entry(pid, employee="outsider").status_code, 404)
        self.assertEqual(self.entry(pid, employee="employee_b").status_code, 404)
        self.assertEqual(self.entry(pid, day="2026-08-08").status_code, 400)
        self.assertEqual(
            self.entry(pid, intervalo_inicio="14:00", intervalo_fim="13:00").status_code, 400
        )
        self.assertEqual(self.entry(pid, entrada="18:00", saida="03:00").status_code, 400)
        with self.app.app_context():
            self.assertEqual(PaymentWorkEntry.query.count(), 0)

    def test_company_and_worksite_isolation(self):
        self.login("admin")
        pid_a = self.make_period()
        pid_b = self.make_period(site="site_b")
        self.login("external")
        page = self.client.get("/admin/pagamentos")
        self.assertEqual(page.status_code, 200)
        self.assertNotIn("Obra A", page.get_data(as_text=True))
        for pid in (pid_a, pid_b):
            self.assertEqual(self.client.get(f"/admin/pagamentos/periodos/{pid}").status_code, 404)
            self.assertEqual(self.entry(pid).status_code, 404)
        self.login("isolated")
        self.assertEqual(self.client.get(f"/admin/pagamentos/periodos/{pid_a}").status_code, 200)
        self.assertEqual(self.client.get(f"/admin/pagamentos/periodos/{pid_b}").status_code, 404)
        self.assertEqual(self.period(site="site_b").status_code, 403)

    def test_no_payment_execution_endpoint_or_monetary_amount(self):
        self.login("admin")
        self.make_period()
        response = self.client.get("/admin/pagamentos")
        self.assertIn("Nenhum PIX é executado", response.get_data(as_text=True))
        self.assertNotIn("chave_pix", PaymentPeriod.__table__.columns.keys())
        self.assertFalse(any(name in PaymentWorkEntry.__table__.columns.keys() for name in ("amount", "pix_key", "paid_at")))


if __name__ == "__main__":
    unittest.main()
