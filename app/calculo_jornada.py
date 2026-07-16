from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from app.jornada import Jornada


@dataclass(frozen=True)
class ResultadoDiario:
    previsto: timedelta
    trabalhado: timedelta
    atraso: timedelta
    saida_antecipada: timedelta
    saldo: timedelta
    registros_incompletos: bool


def _combine(day: date, value: time) -> datetime:
    return datetime.combine(day, value)


def duracao_prevista(jornada: Jornada) -> timedelta:
    inicio = _combine(date.min, jornada.inicio)
    fim = _combine(date.min, jornada.fim)
    total = fim - inicio

    if jornada.intervalo_inicio and jornada.intervalo_fim:
        intervalo_inicio = _combine(date.min, jornada.intervalo_inicio)
        intervalo_fim = _combine(date.min, jornada.intervalo_fim)
        total -= intervalo_fim - intervalo_inicio

    return total


def calcular_dia(jornada: Jornada, registros: list[datetime]) -> ResultadoDiario:
    """Calcula o resultado diário a partir de pares entrada/saída ordenados."""
    ordered = sorted(registros)
    previsto = duracao_prevista(jornada)
    trabalhado = timedelta()

    for index in range(0, len(ordered) - 1, 2):
        entrada = ordered[index]
        saida = ordered[index + 1]
        if saida > entrada:
            trabalhado += saida - entrada

    incompleto = len(ordered) % 2 != 0
    atraso = timedelta()
    saida_antecipada = timedelta()

    if ordered:
        inicio_previsto = _combine(ordered[0].date(), jornada.inicio)
        atraso = max(ordered[0] - inicio_previsto, timedelta())

    if ordered and not incompleto:
        fim_previsto = _combine(ordered[-1].date(), jornada.fim)
        saida_antecipada = max(fim_previsto - ordered[-1], timedelta())

    return ResultadoDiario(
        previsto=previsto,
        trabalhado=trabalhado,
        atraso=atraso,
        saida_antecipada=saida_antecipada,
        saldo=trabalhado - previsto,
        registros_incompletos=incompleto,
    )
