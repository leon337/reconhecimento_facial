from datetime import datetime, timedelta

import pytest

from app.calculo_jornada import (
    ToleranciasJornada,
    calcular_dia,
    duracao_prevista,
)
from app.jornada import parse_jornada


def test_duracao_prevista_desconta_intervalo():
    jornada = parse_jornada("08:00-12:00,13:00-17:00")

    assert duracao_prevista(jornada) == timedelta(hours=8)


def test_calcular_dia_com_jornada_completa_e_saldo_zero():
    jornada = parse_jornada("08:00-12:00,13:00-17:00")
    registros = [
        datetime(2026, 7, 16, 8, 0),
        datetime(2026, 7, 16, 12, 0),
        datetime(2026, 7, 16, 13, 0),
        datetime(2026, 7, 16, 17, 0),
    ]

    resultado = calcular_dia(jornada, registros)

    assert resultado.trabalhado == timedelta(hours=8)
    assert resultado.saldo == timedelta()
    assert resultado.atraso == timedelta()
    assert resultado.saida_antecipada == timedelta()
    assert resultado.registros_incompletos is False


def test_calcular_dia_identifica_atraso_e_saldo_negativo():
    jornada = parse_jornada("08:00-17:00")
    registros = [
        datetime(2026, 7, 16, 8, 15),
        datetime(2026, 7, 16, 17, 0),
    ]

    resultado = calcular_dia(jornada, registros)

    assert resultado.atraso == timedelta(minutes=15)
    assert resultado.trabalhado == timedelta(hours=8, minutes=45)
    assert resultado.saldo == -timedelta(minutes=15)


def test_calcular_dia_identifica_hora_extra():
    jornada = parse_jornada("08:00-17:00")
    registros = [
        datetime(2026, 7, 16, 8, 0),
        datetime(2026, 7, 16, 18, 0),
    ]

    resultado = calcular_dia(jornada, registros)

    assert resultado.saldo == timedelta(hours=1)


def test_calcular_dia_marca_registro_incompleto():
    jornada = parse_jornada("08:00-17:00")

    resultado = calcular_dia(jornada, [datetime(2026, 7, 16, 8, 0)])

    assert resultado.trabalhado == timedelta()
    assert resultado.registros_incompletos is True


def test_atraso_de_ate_cinco_minutos_e_tolerado():
    jornada = parse_jornada("08:00-17:00")
    resultado = calcular_dia(
        jornada,
        [datetime(2026, 7, 16, 8, 5), datetime(2026, 7, 16, 17, 5)],
    )

    assert resultado.atraso_bruto == timedelta(minutes=5)
    assert resultado.atraso == timedelta()
    assert resultado.saldo == timedelta()


def test_hora_extra_abaixo_de_dez_minutos_nao_e_contabilizada():
    jornada = parse_jornada("08:00-17:00")
    resultado = calcular_dia(
        jornada,
        [datetime(2026, 7, 16, 8, 0), datetime(2026, 7, 16, 17, 9)],
    )

    assert resultado.saldo_bruto == timedelta(minutes=9)
    assert resultado.saldo == timedelta()


def test_tolerancias_podem_ser_configuradas():
    jornada = parse_jornada("08:00-17:00")
    tolerancias = ToleranciasJornada(
        atraso=timedelta(minutes=2),
        hora_extra=timedelta(minutes=3),
        saldo=timedelta(minutes=2),
    )

    resultado = calcular_dia(
        jornada,
        [datetime(2026, 7, 16, 8, 4), datetime(2026, 7, 16, 17, 0)],
        tolerancias=tolerancias,
    )

    assert resultado.atraso == timedelta(minutes=4)
    assert resultado.saldo == -timedelta(minutes=4)


def test_tolerancias_negativas_sao_rejeitadas():
    with pytest.raises(ValueError):
        ToleranciasJornada(atraso=-timedelta(minutes=1))
