from datetime import datetime

from sqlalchemy.orm import backref

from app.models import db


class BiometricProfile(db.Model):
    __tablename__ = "biometric_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    encrypted_template = db.Column(db.Text, nullable=False)
    image_object_key = db.Column(db.String(255), nullable=True)
    algorithm_version = db.Column(db.String(40), nullable=False, default="face_recognition-1")
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    user = db.relationship(
        "User",
        backref=backref("biometric_profile", uselist=False, cascade="all, delete-orphan"),
    )
