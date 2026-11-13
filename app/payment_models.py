"""Persistência de conferência semanal, sem valores financeiros ou dados PIX.

Até validação contábil, este módulo registra exclusivamente períodos e jornadas.
Nenhuma operação destes modelos autoriza aprovação ou liquidação de pagamentos.
"""
from datetime import datetime

from app.models import db


class PaymentPeriod(db.Model):
    __tablename__ = "payment_periods"
    __table_args__ = (
        db.UniqueConstraint("scope_key", name="uq_payment_period_scope"),
        db.CheckConstraint("start_date <= end_date", name="ck_payment_period_dates"),
    )

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False, index=True)
    worksite_id = db.Column(db.Integer, db.ForeignKey("worksites.id"), index=True)
    scope_key = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="draft")
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    worksite = db.relationship("Worksite")
    entries = db.relationship("PaymentWorkEntry", back_populates="period", lazy="select")

    @staticmethod
    def key(company_id: int, worksite_id: int | None, start_date, end_date) -> str:
        return f"{company_id}:{worksite_id or 'all'}:{start_date.isoformat()}:{end_date.isoformat()}"


class PaymentWorkEntry(db.Model):
    __tablename__ = "payment_work_entries"
    __table_args__ = (
        db.UniqueConstraint("period_id", "employee_id", "work_date", name="uq_payment_work_day"),
        db.CheckConstraint(
            "worked_minutes > 0 AND worked_minutes <= 1440", name="ck_payment_work_minutes"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    period_id = db.Column(db.Integer, db.ForeignKey("payment_periods.id"), nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False, index=True)
    worksite_id = db.Column(db.Integer, db.ForeignKey("worksites.id"), index=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True)
    work_date = db.Column(db.Date, nullable=False)
    entry_time = db.Column(db.Time, nullable=False)
    break_start = db.Column(db.Time, nullable=False)
    break_end = db.Column(db.Time, nullable=False)
    exit_time = db.Column(db.Time, nullable=False)
    worked_minutes = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    period = db.relationship("PaymentPeriod", back_populates="entries")
    employee = db.relationship("Employee")
