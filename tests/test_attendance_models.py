from datetime import date, datetime

import pytest

from app.attendance_models import AttendanceAdjustment, AttendanceClosure, AttendanceEvent
from app.models import Company, Employee, User, db


def _seed_people(app):
    with app.app_context():
        company = Company(name="Empresa Sintética", slug="empresa-sintetica")
        employee = Employee(name="Colaborador Teste", company=company)
        admin = User(username="admin-fase-95", role="admin", company=company, employee=employee)
        admin.set_password("senha-segura")
        db.session.add_all([company, employee, admin])
        db.session.commit()
        return company.id, employee.id, admin.id


def test_attendance_event_cannot_be_updated(app):
    company_id, employee_id, _ = _seed_people(app)
    with app.app_context():
        event = AttendanceEvent(
            employee_id=employee_id,
            company_id=company_id,
            event_type="clock_in",
            occurred_at=datetime(2026, 7, 19, 8, 0),
        )
        db.session.add(event)
        db.session.commit()
        event.event_type = "clock_out"
        with pytest.raises(ValueError, match="immutable_attendance_event"):
            db.session.commit()
        db.session.rollback()


def test_adjustment_requires_justification(app):
    company_id, employee_id, admin_id = _seed_people(app)
    with app.app_context():
        event = AttendanceEvent(
            employee_id=employee_id,
            company_id=company_id,
            event_type="clock_in",
            occurred_at=datetime(2026, 7, 19, 8, 0),
        )
        db.session.add(event)
        db.session.commit()
        adjustment = AttendanceAdjustment(
            attendance_event_id=event.id,
            requested_by_user_id=admin_id,
            justification=None,
        )
        db.session.add(adjustment)
        with pytest.raises(Exception):
            db.session.commit()
        db.session.rollback()


def test_closure_calculates_overtime_and_is_idempotent(app):
    company_id, employee_id, admin_id = _seed_people(app)
    with app.app_context():
        closure = AttendanceClosure(
            employee_id=employee_id,
            company_id=company_id,
            period_start=date(2026, 7, 1),
            period_end=date(2026, 7, 31),
        )
        closure.close(worked_minutes=10_000, expected_minutes=9_600, user_id=admin_id)
        assert closure.status == "closed"
        assert closure.overtime_minutes == 400
        with pytest.raises(ValueError, match="attendance_period_already_closed"):
            closure.close(worked_minutes=10_000, expected_minutes=9_600, user_id=admin_id)
