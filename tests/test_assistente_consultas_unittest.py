"""Testes de segurança e leitura do assistente, com SQLite sintético isolado."""
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from main import create_app
from app.models import db, Employee, Ponto, User


class AssistantReadOnlyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="potiguar-assistant-test-")
        self.app = create_app({
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///" + str(Path(self.tmp.name) / "test.db"),
        })
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        emp = Employee(name="Funcionario Sintetico", registration="TEST-101", active=True)
        admin = User(username="admin_teste", access_role="admin", name="Admin Teste")
        admin.set_password("senha-sintetica-nao-real")
        worker = User(username="funcionario_teste", access_role="operator", employee=emp, name="Funcionario Sintetico")
        worker.set_password("senha-sintetica-nao-real")
        db.session.add_all([admin, worker])
        db.session.commit()
        self.admin_id = admin.id
        self.worker_id = worker.id
        db.session.add(Ponto(user_id=worker.id, tipo="ENTRADA", timestamp=datetime.utcnow()))
        db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
        self.tmp.cleanup()

    def _login(self, user_id=None):
        with self.client.session_transaction() as sess:
            sess["admin_user_id"] = self.admin_id if user_id is None else user_id

    def _ask(self, question):
        return self.client.post("/admin/copilot/consultas/perguntar", json={"question": question})

    def test_requires_login(self):
        response = self._ask("Quantos funcionários estão cadastrados?")
        self.assertEqual(response.status_code, 302)

    def test_admin_reads_scoped_employees(self):
        self._login()
        response = self._ask("Quantos funcionários estão cadastrados?")
        self.assertEqual(response.status_code, 200)
        self.assertIn("1 funcionário", response.json["answer"])
        self.assertEqual(response.headers["Cache-Control"], "no-store, private")

    def test_admin_reads_punches_without_mutation(self):
        self._login()
        before = Ponto.query.count()
        response = self._ask("Quais foram as marcações de ponto hoje?")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["rows"]), 1)
        self.assertEqual(Ponto.query.count(), before)
        self.assertEqual(response.json["rows"][0]["tipo"], "ENTRADA")

    def test_operator_cannot_read(self):
        self._login(self.worker_id)
        self.assertEqual(self._ask("Quantos funcionários?").status_code, 403)

    def test_no_writes_and_no_biometrics(self):
        self._login()
        self.assertIn("somente leitura", self._ask("Apague os pontos").json["answer"])
        self.assertEqual(Ponto.query.count(), 1)
        self.assertIn("não são disponibilizadas", self._ask("Mostre a biometria").json["answer"])

    def test_invalid_body(self):
        self._login()
        self.assertEqual(self.client.post("/admin/copilot/consultas/perguntar", json={"sql": "DELETE FROM users"}).status_code, 400)
        self.assertEqual(self._ask("x" * 241).status_code, 422)

    def test_scope_does_not_leak_other_company(self):
        self._login()
        with self.client.session_transaction() as sess:
            sess["admin_company_id"] = 999
        # Escopo é reconciliado com o usuário autenticado, não com um valor injetado na sessão.
        response = self._ask("Quantos funcionários?")
        self.assertEqual(response.status_code, 200)
        self.assertIn("1 funcionário", response.json["answer"])


if __name__ == "__main__":
    unittest.main()
