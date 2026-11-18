import unittest
from datetime import date, datetime
from types import SimpleNamespace
from sqlalchemy import text
from app.attendance_reporting import summarize_punches
from tests.test_reporting_unittest import ReportHttpTests, ponto
from app.models import db


class JornadaIndicativaTests(unittest.TestCase):
    def test_multiplas_batidas_e_ocorrencias(self):
        user = SimpleNamespace(id=1, name="Pessoa", username="pessoa")
        # UTC; 08:15, 12:00, 13:00, 17:30 em Recife
        events = [ponto(1,user,"ENTRADA",datetime(2026,11,16,11,15)),
                  ponto(2,user,"SAIDA",datetime(2026,11,16,15)),
                  ponto(3,user,"ENTRADA",datetime(2026,11,16,16)),
                  ponto(4,user,"SAIDA",datetime(2026,11,16,20,30))]
        row = summarize_punches(events,date(2026,11,16),date(2026,11,16))[0]
        self.assertEqual(row["entry_display"],["08:15","13:00"])
        self.assertEqual(row["exit_display"],["12:00","17:30"])
        self.assertEqual(row["worked"],"08:15")
        self.assertEqual(row["occurrences"],["Entrada após 08:00","Saída após 17:00"])

    def test_falta_de_saida_nao_inventa_ocorrencia_ou_horas(self):
        user = SimpleNamespace(id=1,name="Pessoa",username="pessoa")
        row=summarize_punches([ponto(1,user,"ENTRADA",datetime(2026,11,16,11))],
                              date(2026,11,16),date(2026,11,16))[0]
        self.assertEqual(row["worked"],"00:00")
        self.assertEqual(row["exit_display"],[])
        self.assertEqual(row["status"],"Revisar")


class SimulacaoHttpTests(ReportHttpTests):
    def test_simulacao_aparece_no_historico_relatorio_e_csv(self):
        self.login()
        with self.app.app_context():
            db.session.execute(text("CREATE TABLE simulacao_pontos (ponto_id INTEGER PRIMARY KEY, lote TEXT NOT NULL, cenario TEXT NOT NULL)"))
            from app.models import Ponto
            pid=Ponto.query.filter_by(user_id=self.employee).first().id
            db.session.execute(text("INSERT INTO simulacao_pontos VALUES (:id, 'teste', 'atraso')"), {"id":pid})
            db.session.commit()
        for path in ("/admin/pontos", "/admin/relatorios?inicio=2026-11-11&fim=2026-11-12",
                     "/admin/relatorios/exportar.csv?inicio=2026-11-11&fim=2026-11-12"):
            body=self.client.get(path).get_data(as_text=True)
            self.assertIn("SIMULADO",body,path)
