"""Configuração de referência operacional; regras ausentes permanecem pendentes."""
import os
from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True)
class ShiftPolicy:
    start: time
    end: time
    tolerance_minutes: int | None
    break_minutes: int | None
    working_days: tuple[int, ...] | None


def _clock(name, default):
    value=os.environ.get(name,default)
    try:
        result=time.fromisoformat(value)
        if result.second or result.microsecond or result.tzinfo:
            raise ValueError
        return result
    except ValueError as exc:
        raise ValueError(f"{name} deve estar no formato HH:MM") from exc


def _optional_minutes(name, limit):
    value=os.environ.get(name,"").strip()
    if not value:
        return None
    if not value.isdigit() or int(value)>limit:
        raise ValueError(f"{name} inválido")
    return int(value)


def reference_policy():
    start=_clock("POTIGUAR_JORNADA_INICIO","08:00")
    end=_clock("POTIGUAR_JORNADA_FIM","17:00")
    if start >= end:
        raise ValueError("Jornada de referência deve iniciar antes de terminar")
    raw=os.environ.get("POTIGUAR_JORNADA_DIAS","").strip()
    days=None
    if raw:
        if any(x not in {"0","1","2","3","4","5","6"} for x in raw.split(",")):
            raise ValueError("POTIGUAR_JORNADA_DIAS deve usar 0 a 6")
        days=tuple(sorted({int(x) for x in raw.split(",")}))
    return ShiftPolicy(start,end,
                       _optional_minutes("POTIGUAR_JORNADA_TOLERANCIA_MIN",120),
                       _optional_minutes("POTIGUAR_JORNADA_INTERVALO_MIN",480),days)
