"""Regressões dos relatórios de ponto: escopo, datas, CSV, pares e inconsistências."""
import csv
import io
import unittest
from datetime import datetime
from types import SimpleNamespace

from main import create_app
from app.attendance_reporting import summarize_punches
from app.models import db, Company, Employee, User, Ponto
from app.rbac import AccessRole


def ponto(idx, user, kind, utc):
    return SimpleNamespace(id=idx, user_id=user.id, user=user, tipo=kind, timestamp=utc)


class ReportUnitTests(unittest.TestCase):
    def test_unpaired_entries_never_count_hours(self):
        person=SimpleNamespace(id=1,name="Teste",username="teste")
        events=[ponto(1,person,"ENTRADA",datetime(2026,11,12,2,58)),
                ponto(2,person,"ENTRADA",datetime(2026,11,12,2,59))]
        result=summarize_punches(events,datetime(2026,11,11).date(),datetime(2026,11,12).date())
        self.assertEqual(sum(r["seconds"] for r in result),0)
        self.assertTrue(any(r["issues"] for r in result))

    def test_cross_midnight_pair_credited_to_entry_date(self):
        person=SimpleNamespace(id=1,name="Teste",username="teste")
        events=[ponto(1,person,"ENTRADA",datetime(2026,11,12,2,58)),
                ponto(2,person,"SAIDA",datetime(2026,11,12,11,58))]
        result=summarize_punches(events,datetime(2026,11,11).date(),datetime(2026,11,12).date())
        credited=[r for r in result if r["pairs"]]
        self.assertEqual(len(credited),1)
        self.assertEqual(credited[0]["day"].isoformat(),"2026-11-11")
        self.assertEqual(credited[0]["worked"],"09:00")
        self.assertEqual(credited[0]["status"],"Completo")

    def test_long_shift_not_counted(self):
        user=SimpleNamespace(id=1,name="Teste",username="teste")
        result=summarize_punches([
            ponto(1,user,"ENTRADA",datetime(2026,11,10,0,0)),
            ponto(2,user,"SAIDA",datetime(2026,11,12,0,0))],
            datetime(2026,11,9).date(),datetime(2026,11,12).date())
        self.assertEqual(sum(r["seconds"] for r in result),0)


class ReportHttpTests(unittest.TestCase):
    def setUp(self):
        self.app=create_app({
            "TESTING":True,
            "SECRET_KEY":"reports-test-key",
            "SQLALCHEMY_DATABASE_URI":"sqlite:///:memory:",
            "WTF_CSRF_ENABLED":False,
            "AUTO_CREATE_SCHEMA":True,
        })
        self.client=self.app.test_client()
        with self.app.app_context():
            admin=User(username="admin-reports",name="Admin",access_role=AccessRole.ADMIN.value)
            admin.set_password("test-only-password")
            emp=Employee(name="E2E de Teste")
            staff=User(username="e2e.teste",name="E2E de Teste",employee=emp)
            staff.set_password("test-only-password")
            foreign=Company(name="Outra",slug="outra")
            foreign_employee=Employee(name="OUTSIDE",company=foreign)
            foreign_user=User(username="outside",name="OUTSIDE",employee=foreign_employee,company=foreign)
            foreign_user.set_password("test-only-password")
            db.session.add_all([admin,staff,foreign_user])
            db.session.flush()
            db.session.add_all([
                Ponto.from_user(staff,tipo="ENTRADA",timestamp=datetime(2026,11,12,2,58,13)),
                Ponto.from_user(staff,tipo="ENTRADA",timestamp=datetime(2026,11,12,2,59,37)),
                Ponto.from_user(staff,tipo="ENTRADA",timestamp=datetime(2026,11,12,3,1,6)),
                Ponto.from_user(foreign_user,tipo="SAIDA",timestamp=datetime(2026,11,12,3,2,0)),
            ])
            db.session.commit()
            self.admin=admin.id
            self.employee=staff.id

    def login(self):
        with self.client.session_transaction() as session:
            session["admin_user_id"]=self.admin
            session["admin_company_id"]=None
            session["admin_worksite_id"]=None

    def test_private_by_default(self):
        self.assertEqual(self.client.get("/admin/relatorios").status_code,302)
        self.assertEqual(self.client.get("/admin/relatorios/exportar.csv").status_code,302)

    def test_report_shows_incomplete_and_no_worked_hours(self):
        self.login()
        page=self.client.get("/admin/relatorios?inicio=2026-11-11&fim=2026-11-12")
        self.assertEqual(page.status_code,200)
        body=page.get_data(as_text=True)
        self.assertIn("E2E de Teste",body)
        self.assertNotIn("OUTSIDE",body)
        self.assertIn("00:00",body)
        self.assertIn("Revisar",body)

    def test_csv_uses_recife_and_excludes_foreign_company(self):
        self.login()
        csv_response=self.client.get("/admin/relatorios/exportar.csv?inicio=2026-11-11&fim=2026-11-12")
        self.assertEqual(csv_response.status_code,200)
        self.assertIn("attachment",csv_response.headers["Content-Disposition"])
        self.assertIn("no-store",csv_response.headers["Cache-Control"])
        rows=list(csv.reader(io.StringIO(csv_response.data.decode("utf-8-sig")),delimiter=";"))
        self.assertEqual(len(rows),4)
        self.assertEqual(rows[1][4],"11/11/2026 23:58:13")
        self.assertEqual(rows[3][4],"12/11/2026 00:01:06")
        self.assertFalse(any("OUTSIDE" in str(row) for row in rows))

    def test_no_direct_access_to_other_employee(self):
        self.login()
        self.assertEqual(self.client.get("/admin/relatorios?funcionario=999").status_code,404)

    def test_invalid_ranges(self):
        self.login()
        for query in ("inicio=wrong","inicio=2026-12-01&fim=2026-11-01",
                      "inicio=2026-01-01&fim=2026-11-12","funcionario=xyz"):
            response=self.client.get("/admin/relatorios?"+query)
            self.assertEqual(response.status_code,400,query)

    def test_csv_formula_protection(self):
        from app.admin.reporting import _safe_csv_cell
        self.assertEqual(_safe_csv_cell("=SUM(A1:A2)"),"'=SUM(A1:A2)")
        self.assertEqual(_safe_csv_cell(" @bad"),"' @bad")
        self.assertEqual(_safe_csv_cell("normal"),"normal")


if __name__=="__main__":
    unittest.main(verbosity=2)
