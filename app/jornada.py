from dataclasses import dataclass
from datetime import time


class JornadaInvalida(ValueError):
    """Indica que a jornada textual não segue um formato suportado."""


@dataclass(frozen=True)
class Jornada:
    inicio: time
    fim: time
    intervalo_inicio: time | None = None
    intervalo_fim: time | None = None

    def __post_init__(self):
        if self.fim <= self.inicio:
            raise JornadaInvalida("O fim da jornada deve ocorrer após o início.")

        has_break_start = self.intervalo_inicio is not None
        has_break_end = self.intervalo_fim is not None
        if has_break_start != has_break_end:
            raise JornadaInvalida("O intervalo deve possuir início e fim.")

        if has_break_start and not (
            self.inicio < self.intervalo_inicio < self.intervalo_fim < self.fim
        ):
            raise JornadaInvalida("O intervalo deve estar dentro da jornada.")


def _parse_time(value: str) -> time:
    try:
        hour_text, minute_text = value.strip().split(":", maxsplit=1)
        return time(hour=int(hour_text), minute=int(minute_text))
    except (TypeError, ValueError) as exc:
        raise JornadaInvalida(f"Horário inválido: {value!r}.") from exc


def parse_jornada(value: str) -> Jornada:
    """Converte jornadas legadas em uma estrutura validada.

    Formatos suportados:
    - ``08:00-17:00``
    - ``08:00-12:00,13:00-17:00``
    """
    if not value or not value.strip():
        raise JornadaInvalida("A jornada não pode estar vazia.")

    periods = [period.strip() for period in value.split(",")]
    if len(periods) not in {1, 2}:
        raise JornadaInvalida("Use um ou dois períodos de trabalho.")

    try:
        first_start, first_end = periods[0].split("-", maxsplit=1)
    except ValueError as exc:
        raise JornadaInvalida("Período de jornada inválido.") from exc

    if len(periods) == 1:
        return Jornada(inicio=_parse_time(first_start), fim=_parse_time(first_end))

    try:
        second_start, second_end = periods[1].split("-", maxsplit=1)
    except ValueError as exc:
        raise JornadaInvalida("Segundo período de jornada inválido.") from exc

    return Jornada(
        inicio=_parse_time(first_start),
        intervalo_inicio=_parse_time(first_end),
        intervalo_fim=_parse_time(second_start),
        fim=_parse_time(second_end),
    )
