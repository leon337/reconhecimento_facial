import unittest
from datetime import date, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import patch
from app.attendance_reporting import summarize_punches


class LimitesEIntervaloTests(unittest.TestCase):
    def row(self, marks):
        user=SimpleNamespace(id=1,name="Teste",username="teste")
        day=date(2026,11,16)
        points=[]
        for index,(hour,minute,second,kind) in enumerate(marks,1):
            local=datetime(2026,11,16,hour,minute,second)
            points.append(SimpleNamespace(id=index,user_id=1,user=user,tipo=kind,
                                          timestamp=local+timedelta(hours=3)))
        return summarize_punches(points,day,day)[0]

    @patch.dict("os.environ", {}, clear=True)
    def test_five_minutes_each_and_ten_daily_are_not_exceeded(self):
        row=self.row([(8,5,0,"ENTRADA"),(12,0,0,"SAIDA"),(13,0,0,"ENTRADA"),(17,5,0,"SAIDA")])
        self.assertEqual(row["tolerance_display"],"Variações dentro da referência — conferir")
        self.assertEqual(row["interval_display"],"01:00 registrado")
        self.assertEqual(row["worked"],"08:00")

    @patch.dict("os.environ", {}, clear=True)
    def test_more_than_five_minutes_not_subtracted_from_deviation(self):
        row=self.row([(8,6,0,"ENTRADA"),(12,0,0,"SAIDA"),(13,0,0,"ENTRADA"),(17,0,0,"SAIDA")])
        self.assertIn("Entrada após 08:00",row["occurrences"])
        self.assertEqual(row["tolerance_display"],"Variação fora da referência — conferir")

    @patch.dict("os.environ", {}, clear=True)
    def test_exceeds_daily_sum_even_when_each_within_five(self):
        row=self.row([(8,5,0,"ENTRADA"),(12,4,0,"SAIDA"),(13,2,0,"ENTRADA"),(17,0,0,"SAIDA")])
        self.assertIn("Variações observadas somam mais de 10 min — conferir",row["occurrences"])

    @patch.dict("os.environ", {}, clear=True)
    def test_no_lunch_punch_is_not_invented_or_deducted(self):
        row=self.row([(8,0,0,"ENTRADA"),(17,0,0,"SAIDA")])
        self.assertEqual(row["worked"],"09:00")
        self.assertEqual(row["interval_display"],"Não confirmado")
        self.assertEqual(row["status"],"Revisar")
        self.assertIn("Intervalo não confirmado por marcação",row["issues"])

    @patch.dict("os.environ", {}, clear=True)
    def test_short_break_marked_for_review(self):
        row=self.row([(8,0,0,"ENTRADA"),(12,0,0,"SAIDA"),(12,45,0,"ENTRADA"),(17,0,0,"SAIDA")])
        self.assertEqual(row["interval_display"],"00:45 registrado")
        self.assertIn("Intervalo registrado inferior a 1h — conferir",row["occurrences"])

    @patch.dict("os.environ", {}, clear=True)
    def test_five_minutes_and_one_second_exceeds_per_mark(self):
        row=self.row([(8,5,1,"ENTRADA"),(12,0,0,"SAIDA"),(13,0,0,"ENTRADA"),(17,0,0,"SAIDA")])
        self.assertEqual(row["tolerance_display"],"Variação fora da referência — conferir")
