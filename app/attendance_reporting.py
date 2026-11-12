"""Leitura conservadora de pares entrada/saída, sem inferências de folha de pagamento."""
from collections import defaultdict
from datetime import timezone
from zoneinfo import ZoneInfo

RECIFE = ZoneInfo("America/Recife")
MAX_SHIFT_SECONDS = 24 * 3600


def summarize_punches(punches, start_day, end_day):
    """Considera horas somente quando a sequência é inequívoca e a duração <= 24h.

    Credita cada par ao dia LOCAL da ENTRADA, inclusive em turnos noturnos.
    Sequências inconsistentes não viram horas trabalhadas.
    """
    summaries = {}
    pending = {}
    for point in sorted(punches, key=lambda p: (p.timestamp, p.id)):
        user_id = point.user_id
        local_day = point.timestamp.replace(tzinfo=timezone.utc).astimezone(RECIFE).date()
        key = (user_id, local_day)
        if key not in summaries:
            summaries[key] = {
                "user_id": user_id,
                "user": point.user,
                "day": local_day,
                "entries": 0,
                "exits": 0,
                "pairs": 0,
                "seconds": 0,
                "issues": set(),
            }
        row = summaries[key]
        if point.tipo == "ENTRADA":
            row["entries"] += 1
            previous = pending.get(user_id)
            if previous is not None:
                previous_key, previous_point, _ = previous
                summaries[previous_key]["issues"].add("Entrada anterior sem saída")
                row["issues"].add("Entradas consecutivas")
                pending[user_id] = (key, point, True)
            else:
                pending[user_id] = (key, point, False)
        elif point.tipo == "SAIDA":
            row["exits"] += 1
            previous = pending.pop(user_id, None)
            if previous is None:
                row["issues"].add("Saída sem entrada")
                continue
            entry_key, entry, ambiguous = previous
            duration = (point.timestamp - entry.timestamp).total_seconds()
            if ambiguous:
                summaries[entry_key]["issues"].add("Sequência ambígua")
                row["issues"].add("Sequência ambígua")
            elif 0 < duration <= MAX_SHIFT_SECONDS:
                summaries[entry_key]["pairs"] += 1
                summaries[entry_key]["seconds"] += duration
            else:
                summaries[entry_key]["issues"].add("Intervalo inválido")
                row["issues"].add("Intervalo inválido")
        else:
            row["issues"].add("Tipo desconhecido")

    for key, _, _ in pending.values():
        summaries[key]["issues"].add("Entrada sem saída")

    result = []
    for row in summaries.values():
        if start_day <= row["day"] <= end_day:
            row["worked"] = f'{int(row["seconds"] // 3600):02d}:{int(row["seconds"] % 3600 // 60):02d}'
            row["status"] = "Revisar" if row["issues"] else ("Completo" if row["pairs"] else "Sem par")
            row["issues"] = sorted(row["issues"])
            result.append(row)
    return sorted(result, key=lambda r: (r["day"], r["user"].name or r["user"].username, r["user_id"]), reverse=True)
