from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Mapping

from app.calculo_jornada import ResultadoDiario


@dataclass(frozen=True)
class ResumoBancoHoras:
    saldo_anterior: timedelta
    creditos: timedelta
    debitos: timedelta
    saldo_periodo: timedelta
    saldo_acumulado: timedelta
    dias_processados: int
    dias_pendentes: tuple[date, ...]


@dataclass(frozen=True)
class FechamentoMensal:
    ano: int
    mes: int
    saldo_anterior: timedelta
    creditos: timedelta
    debitos: timedelta
    saldo_mes: timedelta
    saldo_acumulado: timedelta
    dias_processados: int
    fechado_em: datetime


def consolidar_banco_horas(resultados: Mapping[date, ResultadoDiario], saldo_anterior: timedelta = timedelta()) -> ResumoBancoHoras:
    creditos = timedelta()
    debitos = timedelta()
    dias_processados = 0
    dias_pendentes = []

    for dia, resultado in sorted(resultados.items()):
        if resultado.registros_incompletos:
            dias_pendentes.append(dia)
            continue
        dias_processados += 1
        if resultado.saldo > timedelta():
            creditos += resultado.saldo
        elif resultado.saldo < timedelta():
            debitos += abs(resultado.saldo)

    saldo_periodo = creditos - debitos
    return ResumoBancoHoras(saldo_anterior, creditos, debitos, saldo_periodo, saldo_anterior + saldo_periodo, dias_processados, tuple(dias_pendentes))


def fechar_mes(ano: int, mes: int, resultados: Mapping[date, ResultadoDiario], saldo_anterior: timedelta = timedelta(), fechado_em: datetime | None = None) -> FechamentoMensal:
    if mes < 1 or mes > 12:
        raise ValueError("O mês deve estar entre 1 e 12.")
    if any(dia.year != ano or dia.month != mes for dia in resultados):
        raise ValueError("Todos os resultados devem pertencer ao mês informado.")

    resumo = consolidar_banco_horas(resultados, saldo_anterior)
    if resumo.dias_pendentes:
        raise ValueError("Não é possível fechar o mês com registros incompletos.")

    return FechamentoMensal(ano, mes, resumo.saldo_anterior, resumo.creditos, resumo.debitos, resumo.saldo_periodo, resumo.saldo_acumulado, resumo.dias_processados, fechado_em or datetime.now())
