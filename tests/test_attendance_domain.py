from datetime import datetime, timedelta

import pytest

from app.attendance import AttendanceEventType, AttendanceMark, summarize_marks, validate_mark_sequence


def test_complete_shift_summary():
    start = datetime(2026, 7, 19, 8, 0)
    marks = [
        AttendanceMark(AttendanceEventType.CLOCK_IN, start),
        AttendanceMark(AttendanceEventType.BREAK_START, start + timedelta(hours=4)),
        AttendanceMark(AttendanceEventType.BREAK_END, start + timedelta(hours=5)),
        AttendanceMark(AttendanceEventType.CLOCK_OUT, start + timedelta(hours=9)),
    ]

    summary = summarize_marks(marks)

    assert summary.break_minutes == 60
    assert summary.worked_minutes == 480
    assert summary.first_clock_in == start
    assert summary.last_clock_out == start + timedelta(hours=9)


def test_invalid_sequence_is_rejected():
    marks = [AttendanceMark(AttendanceEventType.CLOCK_OUT, datetime(2026, 7, 19, 8, 0))]

    with pytest.raises(ValueError, match="invalid_attendance_sequence"):
        validate_mark_sequence(marks)


def test_times_must_be_strictly_increasing():
    moment = datetime(2026, 7, 19, 8, 0)
    marks = [
        AttendanceMark(AttendanceEventType.CLOCK_IN, moment),
        AttendanceMark(AttendanceEventType.BREAK_START, moment),
    ]

    with pytest.raises(ValueError, match="attendance_times_not_increasing"):
        validate_mark_sequence(marks)
