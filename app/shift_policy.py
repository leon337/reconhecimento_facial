"""Referência indicativa de jornada; não é motor de folha."""
import os
from dataclasses import dataclass
from datetime import datetime, time


@dataclass(frozen=True)
class ShiftPolicy:
    start: time
    end: time
    break_start: time
    break_end: time
    tolerance_minutes: int
    daily_tolerance_minutes: int
    working_days: tuple[int, ...] | None

    @property
    def break_minutes(self):
        day=datetime(2000,1,1)
        return int((datetime.combine(day,self.break_end)-datetime.combine(day,self.break_start)).total_seconds()//60)


def _clock(name, default):
    value=os.environ.get(name,default)
    try:
        result=time.fromisoformat(value)
        if result.second or result.microsecond or result.tzinfo:
            raise ValueError
        return result
    except ValueError as exc:
        raise ValueError(f"{name} deve estar no formato HH:MM") from exc


def reference_policy():
    start=_clock("POTIGUAR_JORNADA_INICIO","08:00")
    end=_clock("POTIGUAR_JORNADA_FIM","17:00")
    pause_start=_clock("POTIGUAR_INTERVALO_INICIO","12:00")
    pause_end=_clock("POTIGUAR_INTERVALO_FIM","13:00")
    if not start < pause_start < pause_end < end:
        raise ValueError("Jornada e intervalo de referência inválidos")
    raw=os.environ.get("POTIGUAR_JORNADA_DIAS","").strip()
    days=None
    if raw:
        if any(x not in {"0","1","2","3","4","5","6"} for x in raw.split(",")):
            raise ValueError("POTIGUAR_JORNADA_DIAS deve usar 0 a 6")
        days=tuple(sorted({int(x) for x in raw.split(",")}))
    # Referência do art. 58, §1º; apuração e intervalo exigem conferência.
    return ShiftPolicy(start,end,pause_start,pause_end,5,10,days)
