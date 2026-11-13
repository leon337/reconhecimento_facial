"""Contrato de pré-análise XLSX; nunca carregar dados privados nos testes."""
import io
import unittest
from zipfile import ZipFile

from main import create_app
from app.models import Company, User, db
from app.payment_import import WorkbookPreviewError, inspect_xlsx
from app.rbac import AccessRole


def synthetic_book(*, hidden=True, refs=True, external=True, macro=False, attack=False):
    data = io.BytesIO()
    with ZipFile(data, "w") as zipfile:
        zipfile.writestr("[Content_Types].xml", "<Types/>")
        visible = '<sheet name="RESUMO" sheetId="1"/>'
        private_tab = '<sheet name="NOME SENSIVEL PRIVADO" sheetId="2" state="hidden"/>' if hidden else ""
        workbook = (
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheets>' + visible + private_tab + '</sheets></workbook>'
        )
        zipfile.writestr("xl/workbook.xml", workbook)
        formula = "<f>#REF!+1</f><v>0</v>" if refs else "<f>1+1</f><v>2</v>"
        xml1 = (
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetData><row r="1"><c r="A1"><is><t>PIX 123.456 PRIVADO</t></is></c>'
            '<c r="B1" t="e"><f>#REF!</f><v>#REF!</v></c>'
            f'<c r="C1">{formula}</c></row></sheetData></worksheet>'
        )
        zipfile.writestr("xl/worksheets/sheet1.xml", xml1)
        if hidden:
            zipfile.writestr(
                "xl/worksheets/sheet2.xml",
                '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                '<sheetData><row><c r="A1"><v>987654321</v></c></row></sheetData></worksheet>',
            )
        if external:
            zipfile.writestr("xl/externalLinks/externalLink1.xml", "<externalLink/>")
        if macro:
            zipfile.writestr("xl/vbaProject.bin", "not executable")
        if attack:
            zipfile.writestr("../escape", "bad")
    return data.getvalue()


class WorkbookPreflightTests(unittest.TestCase):
    def test_hidden_errors_external_and_no_cell_values(self):
        preview = inspect_xlsx(synthetic_book())
        self.assertEqual((preview.sheets, preview.visible, preview.hidden), (2, 1, 1))
        self.assertEqual(preview.formulas, 2)
        self.assertEqual(preview.broken_references, 2)
        self.assertEqual(preview.formula_errors, 1)
        self.assertEqual(preview.external_links, 1)
        self.assertEqual(preview.cells_examined, 4)
        self.assertTrue(preview.requires_manual_review)
        self.assertNotIn("PIX", str(preview))
        self.assertNotIn("NOME SENSIVEL", str(preview))

    def test_clean_workbook_has_no_formula_risk(self):
        preview = inspect_xlsx(synthetic_book(hidden=False, refs=False, external=False))
        self.assertEqual(preview.formulas, 2)
        self.assertEqual(preview.broken_references, 1)  # synthetic cached #REF! in B1
        self.assertEqual(preview.hidden, 0)

    def test_rejects_invalid_zip_and_active_parts(self):
        for source in (b"", b"not an xlsx", synthetic_book(macro=True), synthetic_book(attack=True)):
            with self.assertRaises(WorkbookPreviewError):
                inspect_xlsx(source)

    def test_maximum_source_size(self):
        with self.assertRaises(WorkbookPreviewError):
            inspect_xlsx(b"0" * (12 * 1024 * 1024 + 1))


class WorkbookPreflightHttpTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "synthetic-import-preview",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
            "AUTO_CREATE_SCHEMA": True,
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            company = Company(name="Empresa somente de teste", slug="test-import")
            admin = User(username="test-import-admin", access_role=AccessRole.ADMIN.value, company=company)
            auditor = User(username="test-import-auditor", access_role=AccessRole.AUDITOR.value, company=company)
            legacy = User(username="test-import-legacy", access_role=AccessRole.SUPER_ADMIN.value)
            for user in (admin, auditor, legacy):
                user.set_password("only-for-tests")
            db.session.add_all([company, admin, auditor, legacy])
            db.session.commit()
            self.ids = {"admin": admin.id, "auditor": auditor.id, "legacy": legacy.id}

    def login(self, role):
        with self.client.session_transaction() as session:
            session["admin_user_id"] = self.ids[role]

    def upload(self, data, name="exemplo.xlsx"):
        return self.client.post(
            "/admin/pagamentos/importacoes/analisar",
            data={"arquivo": (io.BytesIO(data), name)},
            content_type="multipart/form-data",
        )

    def test_login_and_permissions(self):
        self.assertEqual(self.client.get("/admin/pagamentos/importacoes/analisar").status_code, 302)
        self.login("auditor")
        self.assertEqual(self.client.get("/admin/pagamentos/importacoes/analisar").status_code, 403)
        self.login("legacy")
        self.assertEqual(self.client.get("/admin/pagamentos/importacoes/analisar").status_code, 403)
        self.login("admin")
        self.assertEqual(self.client.get("/admin/pagamentos/importacoes/analisar").status_code, 200)

    def test_preview_returns_only_summary(self):
        self.login("admin")
        response = self.upload(synthetic_book())
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True)[:300])
        self.assertIn("Referências quebradas", response.get_data(as_text=True))
        self.assertNotIn("PIX 123.456", response.get_data(as_text=True))
        self.assertNotIn("NOME SENSIVEL PRIVADO", response.get_data(as_text=True))
        self.assertIn("no-store", response.headers["Cache-Control"])
        with self.app.app_context():
            from app.payment_models import PaymentPeriod, PaymentWorkEntry
            self.assertEqual(PaymentPeriod.query.count(), 0)
            self.assertEqual(PaymentWorkEntry.query.count(), 0)

    def test_invalid_types_and_failed_source(self):
        self.login("admin")
        self.assertEqual(self.upload(b"invalid", "no.xlsx").status_code, 400)
        self.assertEqual(self.upload(synthetic_book(), "bad.xlsm").status_code, 400)

    def test_large_but_permitted_xlsx_exceeds_default_upload_limit(self):
        self.login("admin")
        payload = io.BytesIO()
        # Fonte sintética maior que o limite global de 5 MiB, mas dentro de 12 MiB.
        with ZipFile(payload, "w") as zipfile:
            with ZipFile(io.BytesIO(synthetic_book())) as original:
                for entry in original.infolist():
                    zipfile.writestr(entry.filename, original.read(entry.filename))
            zipfile.writestr("extra_non_xml_payload.bin", b"Q" * (6 * 1024 * 1024))
        response = self.upload(payload.getvalue())
        self.assertEqual(response.status_code, 200)

    def test_upload_csrf_required_when_enabled(self):
        self.login("admin")
        self.app.config["WTF_CSRF_ENABLED"] = True
        self.assertEqual(self.upload(synthetic_book()).status_code, 400)


if __name__ == "__main__":
    unittest.main()
