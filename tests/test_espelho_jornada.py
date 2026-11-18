import unittest
from datetime import date, datetime
from unittest.mock import patch
from types import SimpleNamespace
from app.attendance_reporting import summarize_punches
from app.shift_policy import reference_policy
from tests.test_reporting_unittest import ReportHttpTests, ponto


class PolicyTests(unittest.TestCase):
    @patch.dict("os.environ", {}, clear=True)
    def test_reference_has_no_assumed_break_tolerance_or_weekdays(self):
        p=reference_policy()
        self.assertEqual(p.start.strftime("%H:%M"),"08:00")
        self.assertEqual(p.end.strftime("%H:%M"),"17:00")
        self.assertEqual(p.break_minutes,60)
        self.assertEqual(p.tolerance_minutes,5)
        self.assertEqual(p.daily_tolerance_minutes,10)
        self.assertIsNone(p.working_days)

    @patch.dict("os.environ", {"POTIGUAR_JORNADA_INICIO":"07:00","POTIGUAR_JORNADA_FIM":"16:00",
                              "POTIGUAR_JORNADA_DIAS":"0,1,2,3,4"},clear=True)
    def test_configured_policy_changes_indicators(self):
        user=SimpleNamespace(id=1,name="Teste",username="teste")
        row=summarize_punches([ponto(1,user,"ENTRADA",datetime(2026,11,16,10,5)),
                               ponto(2,user,"SAIDA",datetime(2026,11,16,19,5))],
                              date(2026,11,16),date(2026,11,16))[0]
        self.assertIn("Tolerância diária e intervalo: conferência pendente",row["occurrences"])
        self.assertEqual(reference_policy().working_days,(0,1,2,3,4))

    @patch.dict("os.environ", {"POTIGUAR_JORNADA_DIAS":"0,,2"},clear=True)
    def test_invalid_config_fails_closed(self):
        with self.assertRaises(ValueError): reference_policy()

    def test_night_exit_is_shown_on_entry_day(self):
        user=SimpleNamespace(id=1,name="Teste",username="teste")
        rows=summarize_punches([ponto(1,user,"ENTRADA",datetime(2026,11,17,2)),
                                ponto(2,user,"SAIDA",datetime(2026,11,17,8))],
                               date(2026,11,16),date(2026,11,17))
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["day"],date(2026,11,16))
        self.assertEqual(rows[0]["exit_display"],["05:00"])


class MirrorTests(ReportHttpTests):
    def test_mirror_requires_employee_and_auth_and_scoping(self):
        self.assertEqual(self.client.get("/admin/relatorios/espelho").status_code,302)
        self.login()
        self.assertEqual(self.client.get("/admin/relatorios/espelho").status_code,400)
        self.assertEqual(self.client.get("/admin/relatorios/espelho?funcionario=999").status_code,404)
        response=self.client.get(f"/admin/relatorios/espelho?inicio=2026-11-10&fim=2026-11-12&funcionario={self.employee}")
        self.assertEqual(response.status_code,200)
        body=response.get_data(as_text=True)
        self.assertIn("Espelho de ponto",body)
        self.assertIn("Sem marcações",body)
        self.assertIn("não configurado",body)
        self.assertIn("Revisar",body)
        self.assertNotIn("OUTSIDE",body)
        self.assertEqual(response.headers["Cache-Control"],"no-store, private")
