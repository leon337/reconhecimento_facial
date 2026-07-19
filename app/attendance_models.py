from __future__ import annotations

from datetime import datetime

from sqlalchemy import event

from app.models import db


class WorkSchedule(db.Model):
    __tablename__ = "work_schedules"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False, index=True)
    worksite_id = db.Column(db.Integer, db.ForeignKey("worksites.id"), nullable=True, index=True)
    name = db.Column(db.String(120), nullable=False)
    daily_minutes = db.Column(db.Integer, nullable=False)
    break_minutes = db.Column(db.Integer, nullable=False, default=60)
    active = db.Column(db.Boolean, nullable=False, default=True)


class AttendanceEvent(db.Model):
    __tablename__ = "attendance_events"
    __table_args__ = (
        db.UniqueConstraint("employee_id", "occurred_at", "event_type", name="uq_attendance_event_identity"),
    )

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False, index=True)
    worksite_id = db.Column(db.Integer, db.ForeignKey("worksites.id"), nullable=True, index=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey("work_schedules.id"), nullable=True, index=True)
    event_type = db.Column(db.String(30), nullable=False)
    occurred_at = db.Column(db.DateTime, nullable=False, index=True)
    source = db.Column(db.String(30), nullable=False, default="biometric")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class AttendanceAdjustment(db.Model):
    __tablename__ = "attendance_adjustments"

    id = db.Column(db.Integer, primary_key=True)
    attendance_event_id = db.Column(db.Integer, db.ForeignKey("attendance_events.id"), nullable=False, index=True)
    requested_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    replacement_event_type = db.Column(db.String(30), nullable=True)
    replacement_occurred_at = db.Column(db.DateTime, nullable=True)
    justification = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class AttendanceClosure(db.Model):
    __tablename__ = "attendance_closures"
    __table_args__ = (
        db.UniqueConstraint("employee_id", "period_start", "period_end", name="uq_attendance_closure_period"),
    )

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False, index=True)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="open")
    worked_minutes = db.Column(db.Integer, nullable=False, default=0)
    overtime_minutes = db.Column(db.Integer, nullable=False, default=0)
    closed_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True)

    def close(self, *, worked_minutes: int, expected_minutes: int, user_id: int, now: datetime | None = None) -> None:
        if self.status == "closed":
            raise ValueError("attendance_period_already_closed")
        self.worked_minutes = worked_minutes
        self.overtime_minutes = max(0, worked_minutes - expected_minutes)
        self.status = "closed"
        self.closed_by_user_id = user_id
        self.closed_at = now or datetime.utcnow()


def _reject_mutation(mapper, connection, target):
    raise ValueError("immutable_attendance_event")


event.listen(AttendanceEvent, "before_update", _reject_mutation)
event.listen(AttendanceEvent, "before_delete", _reject_mutation)
event.listen(AttendanceAdjustment, "before_update", _reject_mutation)
event.listen(AttendanceAdjustment, "before_delete", _reject_mutation)
