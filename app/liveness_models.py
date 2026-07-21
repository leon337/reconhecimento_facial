from datetime import datetime

from app.models import db


class LivenessChallenge(db.Model):
    __tablename__ = "liveness_challenges"

    id = db.Column(db.Integer, primary_key=True)
    token_hash = db.Column(db.String(64), nullable=False, unique=True, index=True)
    session_hash = db.Column(db.String(64), nullable=False, index=True)
    purpose = db.Column(db.String(24), nullable=False, index=True)
    subject_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    consumed_at = db.Column(db.DateTime, nullable=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
