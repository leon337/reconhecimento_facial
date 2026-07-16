from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from app.jornada import Jornada


@dataclass(frozen=True)
class ToleranciasJornada:
    atraso: timedelta = timedelta(minutes=5)
    hora_extra: timedelta = timedelta(minutes=10)
    saldo: timedelta = timedelta(minutes=5)

    def __post_init__(self):
        if self.atraso < timedelta() or self.hora_extra < timedelta() or self.saldo < timedelta():
            raise ValueError("As tolerâncias não podem ser negativas.")


@dataclass(frozen=True)
class ResultadoDiario:
    previsto: timedelta
    trabalhado: timedelta
    atraso: timedelta
    saida_antecipada: timedelta
    saldo: timedelta
    registros_incompletos: bool
    atraso_bruto: timedelta
    saida_antecipada_bruta: timedelta
    saldo_bruto: timedelta


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


def _aplicar_tolerancia_positiva(valor: timedelta, limite: timedelta) -> timedelta:
    return timedelta() if valor <= limite else valor


def _aplicar_tolerancia_saldo(valor: timedelta, tolerancias: ToleranciasJornada) -> timedelta:
    if valor > timedelta():
        limite = max(tolerancias.hora_extra, tolerancias.saldo)
        return timedelta() if valor < limite else valor

    if valor < timedelta():
        return timedelta() if abs(valor) <= tolerancias.saldo else valor

    return timedelta()


def calcular_dia(
    jornada: Jornada,
    registros: list[datetime],
    tolerancias: ToleranciasJornada | None = None,
) -> ResultadoDiario:
    """Calcula o resultado diário e preserva valores brutos para auditoria."""
    tolerancias = tolerancias or ToleranciasJornada()
    ordered = sorted(registros)
    previsto = duracao_prevista(jornada)
    trabalhado = timedelta()

    for index in range(0, len(ordered) - 1, 2):
        entrada = ordered[index]
        saida = ordered[index + 1]
        if saida > entrada:
            trabalhado += saida - entrada

    incompleto = len(ordered) % 2 != 0
    atraso_bruto = timedelta()
    saida_antecipada_bruta = timedelta()

    if ordered:
        inicio_previsto = _combine(ordered[0].date(), jornada.inicio)
        atraso_bruto = max(ordered[0] - inicio_previsto, timedelta())

    if ordered and not incompleto:
        fim_previsto = _combine(ordered[-1].date(), jornada.fim)
        saida_antecipada_bruta = max(fim_previsto - ordered[-1], timedelta())

    saldo_bruto = trabalhado - previsto

    return ResultadoDiario(
        previsto=previsto,
        trabalhado=trabalhado,
        atraso=_aplicar_tolerancia_positiva(atraso_bruto, tolerancias.atraso),
        saida_antecipada=_aplicar_tolerancia_positiva(
            saida_antecipada_bruta,
            tolerancias.saldo,
        ),
        saldo=_aplicar_tolerancia_saldo(saldo_bruto, tolerancias),
        registros_incompletos=incompleto,
        atraso_bruto=atraso_bruto,
        saida_antecipada_bruta=saida_antecipada_bruta,
        saldo_bruto=saldo_bruto,
    )
