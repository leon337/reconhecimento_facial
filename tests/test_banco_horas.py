from datetime import date, datetime, timedelta

import pytest

from app.banco_horas import consolidar_banco_horas, fechar_mes
from app.calculo_jornada import calcular_dia
from app.jornada import parse_jornada


def _resultado(dia: int, entrada: tuple[int, int], saida: tuple[int, int]):
    jornada = parse_jornada("08:00-17:00")
    registros = [
        datetime(2026, 7, dia, entrada[0], entrada[1]),
        datetime(2026, 7, dia, saida[0], saida[1]),
    ]
    return calcular_dia(jornada, registros)


def test_banco_de_horas_usa_somente_saldo_tratado_pelas_tolerancias():
    resultados = {
        date(2026, 7, 1): _resultado(1, (8, 0), (17, 9)),
        date(2026, 7, 2): _resultado(2, (8, 0), (17, 20)),
    }

    resumo = consolidar_banco_horas(resultados)

    assert resultados[date(2026, 7, 1)].saldo_bruto == timedelta(minutes=9)
    assert resultados[date(2026, 7, 1)].saldo == timedelta()
    assert resumo.creditos == timedelta(minutes=20)
    assert resumo.saldo_periodo == timedelta(minutes=20)


def test_banco_de_horas_calcula_creditos_debitos_e_saldo_acumulado():
    resultados = {
        date(2026, 7, 1): _resultado(1, (8, 0), (17, 30)),
        date(2026, 7, 2): _resultado(2, (8, 20), (17, 0)),
    }

    resumo = consolidar_banco_horas(resultados, saldo_anterior=timedelta(hours=1))

    assert resumo.creditos == timedelta(minutes=30)
    assert resumo.debitos == timedelta(minutes=20)
    assert resumo.saldo_periodo == timedelta(minutes=10)
    assert resumo.saldo_acumulado == timedelta(hours=1, minutes=10)
    assert resumo.dias_processados == 2


def test_registro_incompleto_fica_pendente_e_nao_altera_saldo():
    jornada = parse_jornada("08:00-17:00")
    dia = date(2026, 7, 3)
    resultado = calcular_dia(jornada, [datetime(2026, 7, 3, 8, 0)])

    resumo = consolidar_banco_horas({dia: resultado})

    assert resumo.saldo_periodo == timedelta()
    assert resumo.dias_processados == 0
    assert resumo.dias_pendentes == (dia,)


def test_fechamento_mensal_gera_snapshot_com_saldo_acumulado():
    fechado_em = datetime(2026, 8, 1, 9, 0)
    resultados = {
        date(2026, 7, 1): _resultado(1, (8, 0), (17, 30)),
        date(2026, 7, 2): _resultado(2, (8, 15), (17, 0)),
    }

    fechamento = fechar_mes(
        2026,
        7,
        resultados,
        saldo_anterior=timedelta(minutes=10),
        fechado_em=fechado_em,
    )

    assert fechamento.creditos == timedelta(minutes=30)
    assert fechamento.debitos == timedelta(minutes=15)
    assert fechamento.saldo_mes == timedelta(minutes=15)
    assert fechamento.saldo_acumulado == timedelta(minutes=25)
    assert fechamento.dias_processados == 2
    assert fechamento.fechado_em == fechado_em


def test_fechamento_mensal_bloqueia_registros_incompletos():
    jornada = parse_jornada("08:00-17:00")
    resultados = {
        date(2026, 7, 3): calcular_dia(
            jornada,
            [datetime(2026, 7, 3, 8, 0)],
        )
    }

    with pytest.raises(ValueError, match="registros incompletos"):
        fechar_mes(2026, 7, resultados)


def test_fechamento_mensal_rejeita_resultado_de_outro_mes():
    resultados = {date(2026, 8, 1): _resultado(1, (8, 0), (17, 0))}

    with pytest.raises(ValueError, match="mês informado"):
        fechar_mes(2026, 7, resultados)


def test_fechamento_mensal_rejeita_mes_invalido():
    with pytest.raises(ValueError, match="entre 1 e 12"):
        fechar_mes(2026, 13, {})
