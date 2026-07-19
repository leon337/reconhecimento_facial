from datetime import datetime

from sqlalchemy import event
from sqlalchemy.orm import Session

from app.models import db


class AuditEvent(db.Model):
    """Evento de auditoria imutável, sem segredos ou conteúdo biométrico."""

    __tablename__ = "audit_events"

    id = db.Column(db.Integer, primary_key=True)
    occurred_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    request_id = db.Column(db.String(64), nullable=False, index=True)
    action = db.Column(db.String(80), nullable=False, index=True)
    outcome = db.Column(db.String(20), nullable=False, index=True)
    actor_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=True, index=True)
    worksite_id = db.Column(db.Integer, db.ForeignKey("worksites.id"), nullable=True, index=True)
    target_type = db.Column(db.String(80), nullable=True)
    target_id = db.Column(db.String(80), nullable=True)
    remote_addr = db.Column(db.String(64), nullable=True)
    metadata_json = db.Column(db.Text, nullable=True)


@event.listens_for(Session, "before_flush")
def protect_audit_events(session, flush_context, instances):
    for entity in session.dirty.union(session.deleted):
        if isinstance(entity, AuditEvent):
            raise ValueError("audit_event_is_append_only")
