import re
import unittest
from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from app.models import db, Ponto, User
from app.punch_review_models import PunchReview
from app.audit_models import AuditEvent
from app.rbac import AccessRole
from tests.test_reporting_unittest import ReportHttpTests


class OccurrenceSecurityTests(ReportHttpTests):
    def setUp(self):
        super().setUp()
        from cryptography.fernet import Fernet
        self.app.config["ONBOARDING_FERNET_KEY"] = Fernet.generate_key()

    def url(self,subject=None,day="2026-11-11"):
        return f"/admin/ocorrencias/{subject or self.employee}/{day}"

    def payload(self,**values):
        p={"request_key":str(uuid4()),"action":"justificativa","note":"Revisão de teste"}
        p.update(values)
        return p

    def test_access_and_scope(self):
        self.assertEqual(self.client.get("/admin/ocorrencias").status_code,302)
        self.login()
        self.assertEqual(self.client.get("/admin/ocorrencias").status_code,200)
        with self.app.app_context():
            foreign=User.query.filter_by(username="outside").one().id
        self.assertEqual(self.client.get(self.url(foreign)).status_code,404)
        self.assertEqual(self.client.post(self.url(foreign),data=self.payload()).status_code,404)

    def test_justification_is_append_only_and_audited(self):
        self.login()
        with self.app.app_context():
            before=[(p.id,p.tipo,p.timestamp) for p in Ponto.query.order_by(Ponto.id)]
        data=self.payload()
        self.assertEqual(self.client.post(self.url(),data=data).status_code,302)
        self.assertEqual(self.client.post(self.url(),data=data).status_code,409)
        with self.app.app_context():
            after=[(p.id,p.tipo,p.timestamp) for p in Ponto.query.order_by(Ponto.id)]
            self.assertEqual(before,after)
            event=PunchReview.query.one()
            self.assertNotIn("Revisão de teste",event.note)
            from app.admin.onboarding import _open
            self.assertEqual(_open(event.note)["text"],"Revisão de teste")
            self.assertEqual(AuditEvent.query.filter_by(action="punch_review.record").count(),1)
            event.note="alteração proibida"
            with self.assertRaises(ValueError): db.session.commit()
            db.session.rollback()

    def test_proposal_validates_original_and_does_not_apply_it(self):
        self.login()
        with self.app.app_context():
            original=Ponto.query.filter_by(user_id=self.employee).first()
            pid=original.id
            initial=original.timestamp
        data=self.payload(action="proposta_ajuste",point_id=str(pid),
                          proposed_type="ENTRADA",proposed_time="09:15")
        self.assertEqual(self.client.post(self.url(),data=data).status_code,302)
        with self.app.app_context():
            self.assertEqual(db.session.get(Ponto,pid).timestamp,initial)
            self.assertEqual(PunchReview.query.one().proposed_time,"09:15")

    def test_proposal_rejects_other_day_or_user(self):
        self.login()
        with self.app.app_context():
            foreign=User.query.filter_by(username="outside").one()
            foreign_point=Ponto.query.filter_by(user_id=foreign.id).first().id
        data=self.payload(action="proposta_ajuste",point_id=str(foreign_point),
                          proposed_type="SAIDA",proposed_time="17:00")
        self.assertEqual(self.client.post(self.url(),data=data).status_code,404)

    def test_auditor_can_read_but_not_write(self):
        self.login()
        with self.app.app_context():
            user=db.session.get(User,self.admin)
            user.access_role=AccessRole.AUDITOR.value
            db.session.commit()
        self.assertEqual(self.client.get(self.url()).status_code,200)
        self.assertEqual(self.client.post(self.url(),data=self.payload()).status_code,403)

    def test_csrf_is_required_when_enabled(self):
        self.login()
        self.app.config["WTF_CSRF_ENABLED"]=True
        self.assertEqual(self.client.post(self.url(),data=self.payload()).status_code,400)

    def test_four_punch_day_shows_originals_without_creating_new_ones(self):
        self.login()
        with self.app.app_context():
            staff=db.session.get(User,self.employee)
            for kind,hour,minute in (("ENTRADA",11,15),("SAIDA",15,0),
                                     ("ENTRADA",16,0),("SAIDA",20,0)):
                db.session.add(Ponto.from_user(staff,tipo=kind,timestamp=datetime(2026,11,16,hour,minute)))
            db.session.commit()
            before=Ponto.query.count()
        response=self.client.get(self.url(day="2026-11-16"))
        self.assertEqual(response.status_code,200)
        body=response.get_data(as_text=True)
        self.assertIn("08:15:00",body)
        self.assertIn("12:00:00",body)
        self.assertIn("13:00:00",body)
        self.assertIn("17:00:00",body)
        with self.app.app_context(): self.assertEqual(Ponto.query.count(),before)

    def test_missing_key_blocks_writing(self):
        self.login()
        self.app.config.pop("ONBOARDING_FERNET_KEY")
        from unittest.mock import patch
        with patch("app.admin.onboarding._cipher",side_effect=__import__("werkzeug").exceptions.ServiceUnavailable()):
            self.assertEqual(self.client.post(self.url(),data=self.payload()).status_code,503)
        with self.app.app_context(): self.assertEqual(PunchReview.query.count(),0)

    def test_invalid_fields_rejected(self):
        self.login()
        for payload in (self.payload(note=""),self.payload(action="bad"),
                        self.payload(request_key="bad"),
                        self.payload(action="proposta_ajuste",proposed_type="SAIDA",proposed_time="25:99")):
            self.assertEqual(self.client.post(self.url(),data=payload).status_code,400)


if __name__=="__main__":
    unittest.main()
