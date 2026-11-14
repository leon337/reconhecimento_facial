"""Fase 04: prévia de vínculo com a V2 sem decriptar ou importar dados financeiros."""
import io
import unittest
from zipfile import ZipFile

from main import create_app
from app.models import db, Company, Worksite, Employee, User
from app.onboarding_models import EmployeeOnboarding
from app.payment_models import PaymentPeriod, PaymentWorkEntry
from app.rbac import AccessRole
from app.payment_import import inspect_xlsx
from app.payment_mapping import inspect_payment_mapping
from app.payment_v2_link import V2EmployeeRef, simulate_v2_link, STATUS_DESCRIPTIONS


def workbook(names=None, *, merged_header=False):
    names = names if names is not None else [
        "JOÃO DA SILVA", "MARIA SOUZA", "PEDRO ALVES", "ANA COSTA",
        "JULIA MARTINS", "JULIA MARTINS", "ALFREDO MELO", "RICARDO BORGES",
        "PAULO MENDES",
    ]
    headings = [
        ("A3", "FUNCIONÁRIOS"), ("C3", "FUNÇÃO"), ("D3", "DIAS TRAB"),
        ("E3", "HS TRAB"), ("F3", "DIÁRIA"), ("G3", "VALOR TOTAL"),
        ("N3", "TOTAL A PAGAR"), ("P3", "PIX"),
    ]
    strings = [name for _, name in headings] + list(names)
    all_cells = []
    for address, label in headings:
        all_cells.append(f'<c r="{address}" t="s"><v>{strings.index(label)}</v></c>')
    rows = ['<row r="3">' + ''.join(all_cells) + '</row>']
    for index, name in enumerate(names, 4):
        rows.append(
            f'<row r="{index}"><c r="{("B" if merged_header else "A")}{index}" t="s">'
            f'<v>{len(headings)+index-4}</v></c>'
            f'<c r="P{index}" t="inlineStr"><is><t>PIX-PRIVATE-{index}</t></is></c>'
            '</row>'
        )
    rows.append(
        '<row r="15"><c r="A15" t="str"><f>SHOULD_NOT_EXECUTE()</f>'
        '<v>FAKE PRIVADO</v></c></row>'
    )
    content = io.BytesIO()
    with ZipFile(content, "w") as book:
        book.writestr("[Content_Types].xml", "<Types/>")
        book.writestr(
            "xl/workbook.xml",
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheets><sheet name="SEGREDO PRIVADO" sheetId="1"/></sheets></workbook>',
        )
        book.writestr(
            "xl/sharedStrings.xml",
            '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            + ''.join(f'<si><t>{name}</t></si>' for name in strings)
            + '</sst>',
        )
        book.writestr(
            "xl/worksheets/sheet1.xml",
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetData>' + ''.join(rows) + '</sheetData>'
            + ('<mergeCells count="1"><mergeCell ref="A3:B3"/></mergeCells>' if merged_header else '')
            + '</worksheet>',
        )
    return content.getvalue()


class V2PureTests(unittest.TestCase):
    def test_transient_preview_suppresses_personal_data(self):
        source = workbook()
        mapping = inspect_payment_mapping(source, preflight=inspect_xlsx(source))
        self.assertEqual(len(mapping.candidates), 1)
        employees = [
            V2EmployeeRef(1, "João da Silva", True, True),
            V2EmployeeRef(2, "Maria Souza", True, False),
            V2EmployeeRef(3, "Pedro Alves", True, True),
            V2EmployeeRef(4, "Pedro Alves", True, True),
            V2EmployeeRef(5, "Ana Costa", False, True),
            V2EmployeeRef(6, "Julia Martins", True, True),
            V2EmployeeRef(7, "Paulo Mendes", True, True),
        ]
        preview = simulate_v2_link(source, mapping, employees)
        self.assertFalse(preview.can_commit)
        self.assertEqual(preview.examined, 10)
        counts = dict(preview.counts)
        self.assertEqual(counts["v2_match"], 2)
        self.assertEqual(counts["legacy_only"], 1)
        self.assertEqual(counts["ambiguous"], 1)
        self.assertEqual(counts["inactive"], 1)
        self.assertEqual(counts["duplicate_source"], 2)
        self.assertEqual(counts["unmatched"], 2)
        self.assertEqual(counts["invalid_source"], 1)
        self.assertEqual(preview.sample[0].row_number, 4)
        self.assertEqual(preview.sample[-1].status, "invalid_source")
        for private in ("JOÃO", "MARIA", "SILVA", "PIX", "FAKE PRIVADO", "EMPREGADO"):
            self.assertNotIn(private, str(preview))
        self.assertTrue(all(status in STATUS_DESCRIPTIONS for _, status in
                            ((s.status, s.status) for s in preview.sample)))

    def test_merged_header_a3_b3_uses_data_column_b(self):
        source = workbook(names=["João da Silva"], merged_header=True)
        mapping = inspect_payment_mapping(source)
        preview = simulate_v2_link(source, mapping, [
            V2EmployeeRef(1, "João da Silva", True, True)
        ])
        self.assertEqual(preview.data_column, "B")
        self.assertEqual(preview.matched, 1)
        self.assertFalse(preview.can_commit)

    def test_untrusted_name_must_not_normalize_into_existing_identity(self):
        source = workbook(names=["Joao 123 da Silva", "Joao da Silva"])
        mapping = inspect_payment_mapping(source)
        preview = simulate_v2_link(source, mapping, [
            V2EmployeeRef(1, "JOÃO DA SILVA", True, True)
        ])
        self.assertEqual(preview.matched, 1)
        self.assertEqual(dict(preview.counts)["invalid_source"], 2)  # row15 formula + digits

    def test_without_reliable_header_fails_closed(self):
        data = workbook()
        mapping = inspect_payment_mapping(data)
        bad = type(mapping)(mapping.sha256_prefix, (), mapping.inspected_sheet_parts, False, ())
        with self.assertRaises(ValueError):
            simulate_v2_link(data, bad, [])

    def test_no_employee_creation_or_financial_payment(self):
        data = workbook(names=["Teste Pessoa"])
        mapping = inspect_payment_mapping(data)
        result = simulate_v2_link(data, mapping, [])
        self.assertEqual(result.matched, 0)
        self.assertFalse(result.can_commit)


class V2HttpTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True, "SECRET_KEY": "v2-link-test-only",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False, "AUTO_CREATE_SCHEMA": True,
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            company_a = Company(name="Potiguar fictícia A", slug="potiguar-a-ficticia")
            company_b = Company(name="Potiguar fictícia B", slug="potiguar-b-ficticia")
            obra_a = Worksite(name="Obra A", company=company_a)
            obra_b = Worksite(name="Obra B", company=company_a)
            obra_c = Worksite(name="Obra Externa", company=company_b)
            employees = [
                Employee(name="João da Silva", company=company_a, worksite=obra_a),
                Employee(name="Maria Souza", company=company_a, worksite=obra_a),
                Employee(name="Pedro Alves", company=company_a, worksite=obra_a),
                Employee(name="Pedro Alves", company=company_a, worksite=obra_b),
                Employee(name="Ana Costa", company=company_a, worksite=obra_a, active=False),
                Employee(name="Julia Martins", company=company_a, worksite=obra_a),
                Employee(name="Paulo Mendes", company=company_a, worksite=obra_b),
                Employee(name="Ricardo Borges", company=company_b, worksite=obra_c),
            ]
            users = [
                User(username="v2-admin", company=company_a, access_role=AccessRole.ADMIN.value),
                User(username="v2-auditor", company=company_a, access_role=AccessRole.AUDITOR.value),
                User(username="v2-manager", company=company_a, access_role=AccessRole.MANAGER.value),
                User(username="v2-site-admin", company=company_a, worksite=obra_a,
                     access_role=AccessRole.ADMIN.value),
                User(username="v2-other-admin", company=company_b, access_role=AccessRole.ADMIN.value),
                User(username="v2-admin-no-scope", access_role=AccessRole.SUPER_ADMIN.value),
            ]
            for user in users:
                user.set_password("v2-fixture-password")
            db.session.add_all([company_a, company_b, obra_a, obra_b, obra_c] + employees + users)
            db.session.flush()
            for employee in employees:
                if employee.name != "Maria Souza":
                    db.session.add(EmployeeOnboarding(
                        employee_id=employee.id, company_id=employee.company_id,
                        worksite_id=employee.worksite_id,
                        created_by=users[0].id, encrypted_payload="CIPHERTEXT_ONLY_V2",
                    ))
            db.session.commit()
            self.ids = {user.username: user.id for user in users}
            self.worksite_ids = {"a": obra_a.id, "b": obra_b.id, "c": obra_c.id}
            self.employee_count = Employee.query.count()

    def login(self, who):
        with self.client.session_transaction() as session:
            session["admin_user_id"] = self.ids[who]

    def upload(self, obra="", *, mode="2", merged_header=False):
        return self.client.post(
            "/admin/pagamentos/importacoes/analisar",
            data={"arquivo": (io.BytesIO(workbook(merged_header=merged_header)), "dados-ficticios.xlsx"),
                  "mapear": mode, "obra": str(obra)},
            content_type="multipart/form-data",
        )

    def test_admin_v2_link_and_no_write(self):
        self.login("v2-admin")
        page = self.upload()
        self.assertEqual(page.status_code, 200)
        text = page.get_data(as_text=True)
        self.assertIn("Conferência de funcionários com a Potiguar V2", text)
        self.assertIn("Correspondência única na V2", text)
        self.assertIn("Simulação apenas", text)
        for private in ("João da Silva", "Maria Souza", "PIX-PRIVATE", "CIPHERTEXT_ONLY_V2",
                        "SEGREDO PRIVADO", "FAKE PRIVADO"):
            self.assertNotIn(private, text)
        self.assertIn("no-store", page.headers["Cache-Control"])
        with self.app.app_context():
            self.assertEqual(Employee.query.count(), self.employee_count)
            self.assertEqual(PaymentPeriod.query.count(), 0)
            self.assertEqual(PaymentWorkEntry.query.count(), 0)

    def test_merged_header_realistic_format_in_v2_route(self):
        self.login("v2-admin")
        page = self.upload(merged_header=True)
        self.assertEqual(page.status_code, 200)
        body = page.get_data(as_text=True)
        self.assertIn("Coluna de dados identificada: <code>B</code>", body)
        self.assertIn("Correspondência única na V2", body)
        self.assertNotIn("JOÃO DA SILVA", body)
        with self.app.app_context():
            self.assertEqual(PaymentWorkEntry.query.count(), 0)

    def test_permission_scope_and_company_isolation(self):
        self.assertEqual(self.upload().status_code, 302)
        self.login("v2-auditor")
        self.assertEqual(self.upload().status_code, 403)
        self.login("v2-manager")
        self.assertEqual(self.upload().status_code, 403)
        self.login("v2-admin-no-scope")
        self.assertEqual(self.upload().status_code, 403)
        self.login("v2-admin")
        self.assertEqual(self.upload(self.worksite_ids["c"]).status_code, 404)
        self.login("v2-site-admin")
        self.assertEqual(self.upload(self.worksite_ids["b"]).status_code, 403)
        self.assertEqual(self.upload(self.worksite_ids["a"]).status_code, 200)
        self.login("v2-other-admin")
        response = self.upload(self.worksite_ids["c"])
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("João da Silva", response.get_data(as_text=True))

    def test_user_v2_list_has_integrated_link_for_authorized_admin(self):
        self.login("v2-admin")
        self.assertIn("Conferir planilha com cadastro V2",
                      self.client.get("/admin/users").get_data(as_text=True))
        self.login("v2-auditor")
        self.assertNotIn("Conferir planilha com cadastro V2",
                         self.client.get("/admin/users").get_data(as_text=True))

    def test_csrf_required_for_v2_preview(self):
        self.login("v2-admin")
        self.app.config["WTF_CSRF_ENABLED"] = True
        self.assertEqual(self.upload().status_code, 400)


if __name__ == "__main__":
    unittest.main()
