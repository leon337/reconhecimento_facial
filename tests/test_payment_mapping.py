"""Contrato do mapeamento XLSX: somente cabeçalhos, sem valores ou PIX."""
import io
import unittest
from xml.sax.saxutils import escape
from zipfile import ZipFile

from app.payment_import import WorkbookPreviewError, inspect_xlsx
from app.payment_mapping import inspect_payment_mapping
from app.models import Company, User, db
from app.payment_models import PaymentPeriod, PaymentWorkEntry
from app.rbac import AccessRole
from main import create_app


HEADERS = {
    "A3": "FUNCIONÁRIOS", "C3": "FUNÇÃO", "D3": "DIAS TRAB",
    "E3": "HS TRAB ", "F3": "DIÁRIA", "G3": "VALOR TOTAL",
    "H3": "HORAS\nDOM/FER", "I3": "DOM E FERIADO",
    "J3": "TOTAL DOM/FER", "K3": "TOTAL À PAGAR HORAS",
    "L3": "ADICIONAL", "M3": "DESCONTO",
    "N3": "TOTAL A PAGAR", "O3": "TIPO", "P3": "PIX",
}


def synthetic_mapping_book(*, inline=False, extra_total=False, hidden=True, variant="diaria"):
    data = io.BytesIO()
    headers = dict(HEADERS)
    if variant == "hora":
        headers.update({
            "F3": "VALOR UNIT DA HS",
            "H3": "HS TRAB DOM FERIADO",
            "I3": "VALOR UNIT DA HS DOM E FERIADO",
            "J3": "TOTAL HS DOM FERIADO",
        })
    labels = list(headers.values()) + ["CPF PRIVADO NAO MOSTRAR", "PIX 123.456 PRIVADO"]
    meta = list(headers.items())
    if extra_total:
        meta.append(("Q3", "TOTAL A PAGAR"))
    with ZipFile(data, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types/>")
        hidden_sheet = (
            '<sheet name="ABA PRIVADA NAO EXIBIR" sheetId="2" state="hidden"/>'
            if hidden else ""
        )
        archive.writestr(
            "xl/workbook.xml",
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheets><sheet name="SHEET NAO MOSTRAR" sheetId="1"/>' + hidden_sheet +
            "</sheets></workbook>",
        )
        if not inline:
            archive.writestr(
                "xl/sharedStrings.xml",
                '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                + "".join("<si><t>" + escape(value) + "</t></si>" for value in labels)
                + "</sst>",
            )
        cells = []
        for address, value in meta:
            if inline:
                cells.append(
                    f'<c r="{address}" t="inlineStr"><is><t>{escape(value)}</t></is></c>'
                )
            else:
                cells.append(
                    f'<c r="{address}" t="s"><v>{labels.index(value)}</v></c>'
                )
        cells.append(
            '<c r="A4" t="inlineStr"><is><t>EMPREGADO PRIVADO 123</t></is></c>'
        )
        cells.append(
            '<c r="P4" t="inlineStr"><is><t>PIX 123.456 PRIVADO</t></is></c>'
        )
        archive.writestr(
            "xl/worksheets/sheet1.xml",
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetData><row r="3">' + "".join(cells[:-2]) + '</row>'
            '<row r="4">' + "".join(cells[-2:]) + '</row>'
            '</sheetData></worksheet>',
        )
        if hidden:
            archive.writestr(
                "xl/worksheets/sheet2.xml",
                '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                '<sheetData><row r="3"><c r="A3" t="inlineStr">'
                '<is><t>NOME PRIVADO</t></is></c></row></sheetData></worksheet>',
            )
    return data.getvalue()


class MappingParsingTests(unittest.TestCase):
    def test_maps_realistic_header_without_reading_values(self):
        result = inspect_payment_mapping(synthetic_mapping_book())
        self.assertEqual(result.inspected_sheet_parts, 2)
        self.assertEqual(len(result.candidates), 1)
        chosen = result.candidates[0]
        self.assertEqual((chosen.technical_id, chosen.header_row), (1, 3))
        coordinates = {col.field: col.column for col in chosen.fields}
        self.assertEqual(coordinates["employee"], "A")
        self.assertEqual(coordinates["days"], "D")
        self.assertEqual(coordinates["worked_hours"], "E")
        self.assertEqual(coordinates["pix"], "P")
        self.assertEqual(coordinates["total_payable"], "N")
        self.assertEqual(len(coordinates), 15)
        self.assertFalse(chosen.can_import)
        for secret in ("EMPREGADO PRIVADO", "123.456", "ABA PRIVADA", "SHEET NAO MOSTRAR"):
            self.assertNotIn(secret, str(result))
        self.assertTrue(result.requires_manual_review)

    def test_hourly_rate_variant_remains_distinct(self):
        result = inspect_payment_mapping(synthetic_mapping_book(variant="hora"))
        self.assertEqual(len(result.candidates), 1)
        coordinates = {c.field: c.column for c in result.candidates[0].fields}
        self.assertEqual(coordinates["hour_unit"], "F")
        self.assertEqual(coordinates["holiday_hour_unit"], "I")
        self.assertEqual(coordinates["sunday_holiday_total"], "J")
        self.assertNotIn("daily", coordinates)
        self.assertEqual(len(coordinates), 15)
        self.assertFalse(result.candidates[0].can_import)

    def test_inline_strings_and_duplicate_labels(self):
        result = inspect_payment_mapping(synthetic_mapping_book(inline=True, extra_total=True))
        self.assertEqual(len(result.candidates), 1)
        self.assertIn("Total a pagar (rótulo original)", result.candidates[0].ambiguous)
        self.assertIn("P", [c.column for c in result.candidates[0].fields])

    def test_non_candidate_is_not_promoted(self):
        with self.assertRaises(WorkbookPreviewError):
            inspect_payment_mapping(b"invalid zip")
        original = synthetic_mapping_book()
        result = inspect_payment_mapping(original, preflight=inspect_xlsx(original))
        self.assertEqual(result.sha256_prefix, inspect_xlsx(original).sha256_prefix)


class MappingHttpTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True, "SECRET_KEY": "mapping-fixture-only",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False, "AUTO_CREATE_SCHEMA": True,
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            company = Company(name="Empresa Fictícia", slug="empresa-mapeamento-teste")
            admin = User(username="map-admin", company=company, access_role=AccessRole.ADMIN.value)
            auditor = User(username="map-auditor", company=company, access_role=AccessRole.AUDITOR.value)
            legacy = User(username="map-no-company", access_role=AccessRole.SUPER_ADMIN.value)
            for item in (admin, auditor, legacy):
                item.set_password("test-only")
            db.session.add_all((company, admin, auditor, legacy))
            db.session.commit()
            self.ids = {"admin": admin.id, "auditor": auditor.id, "legacy": legacy.id}

    def login(self, role):
        with self.client.session_transaction() as session:
            session["admin_user_id"] = self.ids[role]

    def post(self, *, mapear="1"):
        return self.client.post(
            "/admin/pagamentos/importacoes/analisar",
            data={"arquivo": (io.BytesIO(synthetic_mapping_book()), "completo.xlsx"), "mapear": mapear},
            content_type="multipart/form-data",
        )

    def test_authorization_and_privacy(self):
        self.assertEqual(self.post().status_code, 302)
        self.login("auditor")
        self.assertEqual(self.post().status_code, 403)
        self.login("legacy")
        self.assertEqual(self.post().status_code, 403)
        self.login("admin")
        response = self.post()
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Mapeamento de colunas", html)
        self.assertIn("Total a pagar", html)
        for text in ("PIX 123.456 PRIVADO", "EMPREGADO PRIVADO", "ABA PRIVADA"):
            self.assertNotIn(text, html)
        self.assertIn("no-store", response.headers["Cache-Control"])
        with self.app.app_context():
            self.assertEqual(PaymentPeriod.query.count(), 0)
            self.assertEqual(PaymentWorkEntry.query.count(), 0)

    def test_original_preflight_stays_optional(self):
        self.login("admin")
        response = self.post(mapear="0")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Mapeamento de colunas", response.get_data(as_text=True))

    def test_csrf_is_active_for_mapping(self):
        self.login("admin")
        self.app.config["WTF_CSRF_ENABLED"] = True
        self.assertEqual(self.post().status_code, 400)


if __name__ == "__main__":
    unittest.main()
