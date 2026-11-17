"""Persistência separada para onboarding: rascunhos e detalhes criptografados."""
from datetime import datetime
from app.models import db


class OnboardingDraft(db.Model):
    __tablename__ = 'onboarding_drafts'
    id = db.Column(db.String(36), primary_key=True)
    owner_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), index=True)
    worksite_id = db.Column(db.Integer, db.ForeignKey('worksites.id'), index=True)
    version = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default='draft')
    encrypted_payload = db.Column(db.Text, nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmployeeOnboarding(db.Model):
    __tablename__ = 'employee_onboarding'
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='CASCADE'), primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), index=True)
    worksite_id = db.Column(db.Integer, db.ForeignKey('worksites.id'), index=True)
    encrypted_payload = db.Column(db.Text, nullable=False)
    version = db.Column(db.Integer, nullable=False, default=1)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
