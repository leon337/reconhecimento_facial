"""Leitura conservadora de pares entrada/saída, sem inferências de folha de pagamento."""
from collections import defaultdict
from datetime import time, timezone
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
                "entry_times": [],
                "exit_times": [],
                "point_ids": [],
            }
        row = summaries[key]
        row["point_ids"].append(point.id)
        local_time = point.timestamp.replace(tzinfo=timezone.utc).astimezone(RECIFE)
        if point.tipo == "ENTRADA":
            row["entry_times"].append(local_time)
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
            row["exit_times"].append(local_time)
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
            row["entry_display"] = [t.strftime("%H:%M") for t in row["entry_times"]]
            row["exit_display"] = [t.strftime("%H:%M") for t in row["exit_times"]]
            # Comparação indicativa: jornada 08–17; não calcula folha ou intervalo presumido.
            row["occurrences"] = []
            if row["entry_times"] and row["entry_times"][0].time() > time(8):
                row["occurrences"].append("Entrada após 08:00")
            if row["exit_times"] and row["entry_times"] and not row["issues"]:
                last = row["exit_times"][-1]
                if last.date() == row["day"]:
                    if last.time() < time(17):
                        row["occurrences"].append("Saída antes de 17:00")
                    elif last.time() > time(17):
                        row["occurrences"].append("Saída após 17:00")
            row["status"] = "Revisar" if row["issues"] else ("Completo" if row["pairs"] else "Sem par")
            row["issues"] = sorted(row["issues"])
            result.append(row)
    return sorted(result, key=lambda r: (r["day"], r["user"].name or r["user"].username, r["user_id"]), reverse=True)
