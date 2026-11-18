"""Eventos imutáveis de revisão do ponto; nunca modificam marcações."""
from datetime import datetime
from sqlalchemy import event
from app.models import db


class PunchReview(db.Model):
    __tablename__ = "punch_review_events"
    id = db.Column(db.Integer, primary_key=True)
    request_key = db.Column(db.String(36), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=True, index=True)
    worksite_id = db.Column(db.Integer, db.ForeignKey("worksites.id"), nullable=True, index=True)
    day = db.Column(db.Date, nullable=False, index=True)
    action = db.Column(db.String(32), nullable=False)
    note = db.Column(db.Text, nullable=False)
    point_id = db.Column(db.Integer, db.ForeignKey("pontos.id"), nullable=True)
    proposed_type = db.Column(db.String(10), nullable=True)
    proposed_time = db.Column(db.String(5), nullable=True)
    actor_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


def _immutable(mapper, connection, target):
    raise ValueError("punch_review_is_append_only")


event.listen(PunchReview, "before_update", _immutable)
event.listen(PunchReview, "before_delete", _immutable)
