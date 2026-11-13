"""Apuração estritamente temporal; base remuneratória deliberadamente ausente."""
from datetime import datetime, time


def calculate_worked_minutes(
    entry: time, break_start: time, break_end: time, exit_: time
) -> int:
    """Exige quatro horários completos, ordenados e precisos ao minuto.

    Jornadas noturnas, múltiplos intervalos e regras monetárias serão tratadas
    em fases posteriores, após definição contratual e validação de exemplos.
    """
    values = (entry, break_start, break_end, exit_)
    if any(value.tzinfo is not None for value in values):
        raise ValueError("Informe horários locais sem deslocamento de fuso.")
    if any(value.second or value.microsecond for value in values):
        raise ValueError("Os horários devem ter precisão de minutos.")
    if not (entry < break_start < break_end < exit_):
        raise ValueError("Informe entrada, intervalo e saída em ordem crescente.")
    day = datetime(2000, 1, 1)
    minutes = (
        (datetime.combine(day, break_start) - datetime.combine(day, entry)).seconds
        + (datetime.combine(day, exit_) - datetime.combine(day, break_end)).seconds
    ) // 60
    if not 0 < minutes <= 24 * 60:
        raise ValueError("Jornada inválida.")
    return minutes


def duration_label(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"
