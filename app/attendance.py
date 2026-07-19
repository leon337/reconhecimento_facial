from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AttendanceEventType(str, Enum):
    CLOCK_IN = "clock_in"
    BREAK_START = "break_start"
    BREAK_END = "break_end"
    CLOCK_OUT = "clock_out"


class ClosureStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


@dataclass(frozen=True)
class AttendanceMark:
    kind: AttendanceEventType
    occurred_at: datetime


@dataclass(frozen=True)
class AttendanceSummary:
    worked_minutes: int
    break_minutes: int
    first_clock_in: datetime | None
    last_clock_out: datetime | None


_ALLOWED_NEXT = {
    None: AttendanceEventType.CLOCK_IN,
    AttendanceEventType.CLOCK_IN: AttendanceEventType.BREAK_START,
    AttendanceEventType.BREAK_START: AttendanceEventType.BREAK_END,
    AttendanceEventType.BREAK_END: AttendanceEventType.CLOCK_OUT,
    AttendanceEventType.CLOCK_OUT: None,
}


def validate_mark_sequence(marks: list[AttendanceMark]) -> None:
    previous: AttendanceEventType | None = None
    previous_time: datetime | None = None
    for mark in marks:
        expected = _ALLOWED_NEXT[previous]
        if mark.kind != expected:
            raise ValueError("invalid_attendance_sequence")
        if previous_time is not None and mark.occurred_at <= previous_time:
            raise ValueError("attendance_times_not_increasing")
        previous = mark.kind
        previous_time = mark.occurred_at


def summarize_marks(marks: list[AttendanceMark]) -> AttendanceSummary:
    if not marks:
        return AttendanceSummary(0, 0, None, None)
    validate_mark_sequence(marks)
    clock_in = marks[0].occurred_at
    clock_out = marks[-1].occurred_at if marks[-1].kind == AttendanceEventType.CLOCK_OUT else None
    break_minutes = 0
    if len(marks) >= 3:
        break_minutes = int((marks[2].occurred_at - marks[1].occurred_at).total_seconds() // 60)
    worked_minutes = 0
    if clock_out is not None:
        worked_minutes = int((clock_out - clock_in).total_seconds() // 60) - break_minutes
    return AttendanceSummary(worked_minutes, break_minutes, clock_in, clock_out)
