#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os

from app.infrastructure.backup import configured_backup_directory, create_backup, prune_backups


def main() -> int:
    parser = argparse.ArgumentParser(description="Cria backup PostgreSQL com checksum e manifesto.")
    parser.add_argument("--retention-days", type=int, default=int(os.environ.get("BACKUP_RETENTION_DAYS", "30")))
    args = parser.parse_args()

    destination = configured_backup_directory()
    archive, manifest = create_backup(database_url=os.environ.get("DATABASE_URL"), destination=destination)
    removed = prune_backups(destination, args.retention_days)
    print(f"backup={archive}")
    print(f"manifest={manifest}")
    print(f"removed={len(removed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
