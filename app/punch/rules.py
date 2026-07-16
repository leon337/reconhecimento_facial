from dataclasses import dataclass
from datetime import datetime, timedelta

from app.models import Ponto


@dataclass(frozen=True)
class DuplicatePunchResult:
    blocked: bool
    retry_after_seconds: int


def check_duplicate_punch(
    user_id: int,
    now: datetime,
    window_seconds: int,
) -> DuplicatePunchResult:
    """Bloqueia nova batida quando já existe registro recente do usuário."""
    if window_seconds <= 0:
        return DuplicatePunchResult(False, 0)

    latest = (
        Ponto.query.filter_by(user_id=user_id)
        .order_by(Ponto.timestamp.desc())
        .first()
    )
    if latest is None:
        return DuplicatePunchResult(False, 0)

    elapsed = now - latest.timestamp
    if elapsed < timedelta(0) or elapsed >= timedelta(seconds=window_seconds):
        return DuplicatePunchResult(False, 0)

    remaining = max(1, window_seconds - int(elapsed.total_seconds()))
    return DuplicatePunchResult(True, remaining)
