"""Limite global de sessões Gemini na homologação pública do Potiguar.

Não afeta a aplicação oficial quando POTIGUAR_COPILOT_DEMO_DAILY_LIMIT não está
definida. Controla os custos do ensaio no host, sem armazenar tokens ou falas.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class DemoQuotaReached(RuntimeError):
    pass


class DemoQuotaUnavailable(RuntimeError):
    pass


def reserve_session(instance_path: str, limit: int, *, category: str = "voice") -> int:
    if category not in {"voice", "employee"}:
        raise DemoQuotaUnavailable("Categoria de cota não reconhecida")
    if limit <= 0:
        return 0
    folder = Path(instance_path).resolve()
    if not folder.is_dir():
        raise DemoQuotaUnavailable("Diretório privado da homologação ausente")
    db_path = folder / "copilot-demo-quota.sqlite3"
    today = category + ":" + datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        with sqlite3.connect(str(db_path), timeout=5, isolation_level=None) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS demo_quota "
                "(day TEXT PRIMARY KEY, sessions INTEGER NOT NULL)"
            )
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT sessions FROM demo_quota WHERE day=?", (today,)
            ).fetchone()
            count = int(row[0]) if row else 0
            if count >= limit:
                conn.execute("ROLLBACK")
                raise DemoQuotaReached("Limite diário de sessões de demonstração")
            conn.execute(
                "INSERT INTO demo_quota(day,sessions) VALUES (?,?) "
                "ON CONFLICT(day) DO UPDATE SET sessions=excluded.sessions",
                (today, count + 1),
            )
            conn.execute("COMMIT")
            return limit - count - 1
    except DemoQuotaReached:
        raise
    except (sqlite3.Error, OSError) as exc:
        raise DemoQuotaUnavailable("Limite de homologação indisponível") from exc
