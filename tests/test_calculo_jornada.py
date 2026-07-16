from datetime import datetime, timedelta

from app.calculo_jornada import calcular_dia, duracao_prevista
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
