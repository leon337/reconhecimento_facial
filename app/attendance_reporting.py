"""Leitura conservadora de pares entrada/saída, sem inferências de folha de pagamento."""
from collections import defaultdict
from datetime import timedelta, timezone
from app.shift_policy import reference_policy
from zoneinfo import ZoneInfo

RECIFE = ZoneInfo("America/Recife")
MAX_SHIFT_SECONDS = 24 * 3600


def summarize_punches(punches, start_day, end_day):
    """Considera horas somente quando a sequência é inequívoca e a duração <= 24h.

    Credita cada par ao dia LOCAL da ENTRADA, inclusive em turnos noturnos.
    Sequências inconsistentes não viram horas trabalhadas.
    """
    policy = reference_policy()
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
                if entry_key != key:
                    # A saída noturna pertence à jornada do dia da entrada.
                    row["exit_times"].pop()
                    row["exits"] -= 1
                    row["point_ids"].remove(point.id)
                    summaries[entry_key]["exit_times"].append(local_time)
                    summaries[entry_key]["exits"] += 1
                    summaries[entry_key]["point_ids"].append(point.id)
                    if not row["point_ids"] and not row["issues"]:
                        del summaries[key]
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
            # Variações são indicadores, não descontos nem horas extras.
            row["occurrences"] = []
            row["interval_display"] = "Não confirmado"
            row["tolerance_display"] = "Apuração diária pendente"
            entries, exits = row["entry_times"], row["exit_times"]
            if entries and exits and not row["issues"] and all(t.date() == row["day"] for t in entries + exits):
                first, last = entries[0], exits[-1]
                def seconds_from(value, reference):
                    expected=value.replace(hour=reference.hour, minute=reference.minute, second=0, microsecond=0)
                    return (value-expected).total_seconds()
                entry_delta=seconds_from(first,policy.start)
                exit_delta=seconds_from(last,policy.end)
                deltas=[entry_delta,exit_delta]
                complete_interval=(len(entries)==2 and len(exits)==2 and entries[0] < exits[0] < entries[1] < exits[1])
                if complete_interval:
                    pause=(entries[1]-exits[0]).total_seconds()
                    row["interval_display"] = f"{int(pause//3600):02d}:{int(pause%3600//60):02d} registrado"
                    deltas += [seconds_from(exits[0],policy.break_start),seconds_from(entries[1],policy.break_end)]
                    if pause < policy.break_minutes*60:
                        row["occurrences"].append("Intervalo registrado inferior a 1h — conferir")
                elif row["seconds"] > 6*3600:
                    row["issues"].add("Intervalo não confirmado por marcação")
                daily_exceeded = sum(abs(d) for d in deltas) > policy.daily_tolerance_minutes*60
                individual_exceeded = any(abs(d) > policy.tolerance_minutes*60 for d in deltas)
                if individual_exceeded or daily_exceeded:
                    row["tolerance_display"] = "Variação fora da referência — conferir"
                elif complete_interval:
                    row["tolerance_display"] = "Variações dentro da referência — conferir"
                if abs(entry_delta)>policy.tolerance_minutes*60 or (daily_exceeded and entry_delta != 0):
                    row["occurrences"].append(f"Entrada {'após' if entry_delta>0 else 'antes de'} {policy.start:%H:%M}")
                if abs(exit_delta)>policy.tolerance_minutes*60 or (daily_exceeded and exit_delta != 0):
                    row["occurrences"].append(f"Saída {'após' if exit_delta>0 else 'antes de'} {policy.end:%H:%M}")
                if daily_exceeded:
                    row["occurrences"].append("Variações observadas somam mais de 10 min — conferir")
                if not complete_interval:
                    row["occurrences"].append("Tolerância diária e intervalo: conferência pendente")
            row["status"] = "Revisar" if row["issues"] else ("Completo" if row["pairs"] else "Sem par")
            row["issues"] = sorted(row["issues"])
            result.append(row)
    return sorted(result, key=lambda r: (r["day"], r["user"].name or r["user"].username, r["user_id"]), reverse=True)
