from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.infrastructure.backup import (
    BackupConfigurationError,
    create_backup,
    prune_backups,
    require_postgres_url,
    restore_backup,
    verify_backup,
)


def test_rejects_non_postgresql_url():
    with pytest.raises(BackupConfigurationError):
        require_postgres_url("sqlite:///local.db")


def test_normalizes_legacy_postgres_scheme():
    assert require_postgres_url("postgres://user:pass@db:5432/app").startswith("postgresql://")


def test_creates_manifest_and_verifies_checksum(tmp_path):
    calls = []

    def runner(command, check):
        calls.append(command)
        Path(command[command.index("--file") + 1]).write_bytes(b"synthetic-backup")

    archive, manifest = create_backup(
        database_url="postgresql://user:pass@db:5432/app",
        destination=tmp_path,
        runner=runner,
    )

    assert archive.exists()
    assert manifest.exists()
    assert calls[0][0] == "pg_dump"
    verify_backup(archive, manifest)
    payload = json.loads(manifest.read_text())
    assert payload["database_name"] == "app"
    assert payload["database_host"] == "db"
    assert "pass" not in manifest.read_text()


def test_detects_tampered_archive(tmp_path):
    archive = tmp_path / "database-test.dump"
    archive.write_bytes(b"original")
    manifest = archive.with_suffix(".manifest.json")
    manifest.write_text(json.dumps({"archive_name": archive.name, "sha256": "invalid"}))
    with pytest.raises(RuntimeError, match="Checksum"):
        verify_backup(archive, manifest)


def test_restore_requires_explicit_confirmation(tmp_path):
    archive = tmp_path / "database-test.dump"
    archive.write_bytes(b"synthetic")
    import hashlib
    manifest = archive.with_suffix(".manifest.json")
    manifest.write_text(json.dumps({"archive_name": archive.name, "sha256": hashlib.sha256(b"synthetic").hexdigest()}))

    with pytest.raises(PermissionError):
        restore_backup(
            database_url="postgresql://user:pass@db:5432/app",
            archive=archive,
            manifest_path=manifest,
            confirmation="NO",
            runner=lambda *args, **kwargs: None,
        )


def test_prunes_expired_backup_and_manifest(tmp_path):
    archive = tmp_path / "database-old.dump"
    archive.write_bytes(b"old")
    manifest = archive.with_suffix(".manifest.json")
    manifest.write_text("{}")
    old = datetime.now(timezone.utc) - timedelta(days=31)
    import os
    os.utime(archive, (old.timestamp(), old.timestamp()))

    removed = prune_backups(tmp_path, 30, now=datetime.now(timezone.utc))
    assert removed == [archive]
    assert not archive.exists()
    assert not manifest.exists()
