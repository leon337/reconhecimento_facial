"""Cota atômica e idempotência do modo texto em sidecar isolado, sem PII."""
from __future__ import annotations

import hashlib
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path


class TextQuotaExceeded(RuntimeError):
    pass


class TextReplay(RuntimeError):
    pass


class TextQuotaUnavailable(RuntimeError):
    pass


def reserve_text_turn(instance_path, principal, request_id, *, daily_limit=25,
                      principal_daily_limit=8, source_id="unknown",
                      source_daily_limit=20, min_interval=2.0, clock=None):
    """Uma reserva/uso por request_id. Falhas do provedor não são reembolsadas."""
    if not isinstance(principal, str) or len(principal) > 128 or not principal:
        raise TextQuotaUnavailable("invalid_principal")
    if not isinstance(request_id, str) or len(request_id) > 64:
        raise TextQuotaUnavailable("invalid_id")
    if not isinstance(source_id, str) or not 1 <= len(source_id) <= 128:
        raise TextQuotaUnavailable("invalid_source")
    if not isinstance(daily_limit, int) or not 1 <= daily_limit <= 1000:
        raise TextQuotaUnavailable("invalid_limit")
    if not isinstance(principal_daily_limit, int) or not 1 <= principal_daily_limit <= 1000:
        raise TextQuotaUnavailable("invalid_principal_limit")
    if not isinstance(source_daily_limit, int) or not 1 <= source_daily_limit <= 1000:
        raise TextQuotaUnavailable("invalid_source_limit")
    folder = Path(instance_path).resolve()
    if not folder.is_dir():
        raise TextQuotaUnavailable("no_private_store")
    now = time.time() if clock is None else float(clock())
    day = datetime.fromtimestamp(now, timezone.utc).strftime("%Y-%m-%d")
    actor = hashlib.sha256(principal.encode("utf-8")).hexdigest()
    source = hashlib.sha256(source_id.encode("utf-8")).hexdigest()
    fingerprint = hashlib.sha256((actor + ":" + request_id).encode("utf-8")).hexdigest()
    db_path = folder / "copilot-text-quota.sqlite3"
    try:
        with sqlite3.connect(db_path, timeout=5, isolation_level=None) as conn:
            conn.execute("PRAGMA busy_timeout=5000")
            conn.execute("CREATE TABLE IF NOT EXISTS text_turns "
                         "(fingerprint TEXT PRIMARY KEY, day TEXT NOT NULL, actor TEXT NOT NULL, "
                         "source TEXT NOT NULL, started REAL NOT NULL)")
            conn.execute("CREATE INDEX IF NOT EXISTS text_turns_by_day ON text_turns(day)")
            conn.execute("CREATE INDEX IF NOT EXISTS text_turns_by_actor ON text_turns(actor,day)")
            conn.execute("CREATE INDEX IF NOT EXISTS text_turns_by_source ON text_turns(source,day)")
            conn.execute("BEGIN IMMEDIATE")
            try:
                if conn.execute("SELECT 1 FROM text_turns WHERE fingerprint=?", (fingerprint,)).fetchone():
                    raise TextReplay("request_id já processado")
                global_used = conn.execute(
                    "SELECT COUNT(*) FROM text_turns WHERE day=?", (day,)
                ).fetchone()[0]
                personal = conn.execute(
                    "SELECT COUNT(*), MAX(started) FROM text_turns WHERE actor=? AND day=?",
                    (actor, day),
                ).fetchone()
                source_used = conn.execute(
                    "SELECT COUNT(*) FROM text_turns WHERE source=? AND day=?",
                    (source, day),
                ).fetchone()[0]
                if (global_used >= daily_limit
                        or personal[0] >= min(principal_daily_limit, daily_limit)
                        or source_used >= min(source_daily_limit, daily_limit)):
                    raise TextQuotaExceeded("limite atingido")
                if personal[1] is not None and now - personal[1] < min_interval:
                    raise TextQuotaExceeded("intervalo mínimo")
                conn.execute(
                    "INSERT INTO text_turns(fingerprint,day,actor,source,started) VALUES (?,?,?,?,?)",
                    (fingerprint, day, actor, source, now),
                )
                conn.execute("COMMIT")
            except Exception:
                conn.execute("ROLLBACK")
                raise
    except (TextReplay, TextQuotaExceeded):
        raise
    except (sqlite3.Error, OSError) as exc:
        raise TextQuotaUnavailable("quota indisponível") from None
