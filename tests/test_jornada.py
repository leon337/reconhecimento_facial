import pytest

from app.jornada import JornadaInvalida, parse_jornada


def test_parse_jornada_without_break():
    jornada = parse_jornada("08:00-17:00")

    assert jornada.inicio.hour == 8
    assert jornada.fim.hour == 17
    assert jornada.intervalo_inicio is None
    assert jornada.intervalo_fim is None


def test_parse_jornada_with_break():
    jornada = parse_jornada("08:00-12:00,13:00-17:00")

    assert jornada.inicio.hour == 8
    assert jornada.intervalo_inicio.hour == 12
    assert jornada.intervalo_fim.hour == 13
    assert jornada.fim.hour == 17


@pytest.mark.parametrize(
    "value",
    ["", "08:00", "17:00-08:00", "08:00-18:00,12:00-13:00"],
)
def test_parse_jornada_rejects_invalid_values(value):
    with pytest.raises(JornadaInvalida):
        parse_jornada(value)
