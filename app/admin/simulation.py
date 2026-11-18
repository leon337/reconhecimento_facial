"""Identificação opcional dos pontos de homologação, sem alterar os registros originais."""
from sqlalchemy import bindparam, inspect, text
from app.models import db


def simulated_ids(points):
    ids = [p.id for p in points]
    if not ids or not inspect(db.engine).has_table("simulacao_pontos"):
        return set()
    query = text("SELECT ponto_id FROM simulacao_pontos WHERE ponto_id IN :ids").bindparams(
        bindparam("ids", expanding=True)
    )
    return set(db.session.execute(query, {"ids": ids}).scalars())
