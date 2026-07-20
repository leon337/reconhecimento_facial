from __future__ import annotations

import hashlib
import json
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


class BackupConfigurationError(RuntimeError):
    pass


@dataclass(frozen=True)
class BackupManifest:
    created_at: str
    database_host: str
    database_name: str
    archive_name: str
    sha256: str
    format_version: int = 1


def require_postgres_url(database_url: str | None) -> str:
    if not database_url:
        raise BackupConfigurationError("DATABASE_URL é obrigatória para backup.")
    normalized = database_url.replace("postgres://", "postgresql://", 1)
    parsed = urlparse(normalized)
    if parsed.scheme not in {"postgresql", "postgresql+psycopg2"} or not parsed.hostname or not parsed.path:
        raise BackupConfigurationError("DATABASE_URL deve apontar para PostgreSQL.")
    return normalized


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_backup(*, database_url: str, destination: Path, runner=subprocess.run) -> tuple[Path, Path]:
    normalized = require_postgres_url(database_url)
    destination.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive = destination / f"database-{timestamp}.dump"
    runner(["pg_dump", "--format=custom", "--no-owner", "--no-privileges", "--file", str(archive), normalized], check=True)
    if not archive.is_file() or archive.stat().st_size == 0:
        raise RuntimeError("Backup não foi criado ou está vazio.")

    parsed = urlparse(normalized)
    manifest = BackupManifest(
        created_at=datetime.now(timezone.utc).isoformat(),
        database_host=parsed.hostname or "unknown",
        database_name=parsed.path.lstrip("/"),
        archive_name=archive.name,
        sha256=sha256_file(archive),
    )
    manifest_path = archive.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(asdict(manifest), indent=2, sort_keys=True), encoding="utf-8")
    return archive, manifest_path


def verify_backup(archive: Path, manifest_path: Path) -> None:
    if not archive.is_file() or not manifest_path.is_file():
        raise FileNotFoundError("Arquivo de backup ou manifesto ausente.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("archive_name") != archive.name:
        raise RuntimeError("Manifesto não corresponde ao arquivo informado.")
    if manifest.get("sha256") != sha256_file(archive):
        raise RuntimeError("Checksum do backup inválido.")


def restore_backup(*, database_url: str, archive: Path, manifest_path: Path, confirmation: str, runner=subprocess.run) -> None:
    normalized = require_postgres_url(database_url)
    if confirmation != "RESTORE":
        raise PermissionError("Restauração exige confirmação explícita RESTORE.")
    verify_backup(archive, manifest_path)
    runner(["pg_restore", "--clean", "--if-exists", "--no-owner", "--no-privileges", "--dbname", normalized, str(archive)], check=True)


def prune_backups(destination: Path, retention_days: int, *, now: datetime | None = None) -> list[Path]:
    if retention_days < 1:
        raise ValueError("Retenção deve ser de pelo menos um dia.")
    reference = now or datetime.now(timezone.utc)
    removed: list[Path] = []
    for archive in destination.glob("database-*.dump"):
        modified = datetime.fromtimestamp(archive.stat().st_mtime, tz=timezone.utc)
        if (reference - modified).days >= retention_days:
            manifest = archive.with_suffix(".manifest.json")
            archive.unlink(missing_ok=True)
            manifest.unlink(missing_ok=True)
            removed.append(archive)
    return removed


def configured_backup_directory() -> Path:
    return Path(os.environ.get("BACKUP_DIRECTORY", "/var/backups/controle-ponto"))
