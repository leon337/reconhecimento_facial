#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path

from app.infrastructure.backup import restore_backup


def main() -> int:
    parser = argparse.ArgumentParser(description="Restaura backup PostgreSQL após validar manifesto e checksum.")
    parser.add_argument("archive", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--confirm", required=True, help="Informe RESTORE para autorizar a operação destrutiva.")
    args = parser.parse_args()

    manifest = args.manifest or args.archive.with_suffix(".manifest.json")
    restore_backup(
        database_url=os.environ.get("DATABASE_URL"),
        archive=args.archive,
        manifest_path=manifest,
        confirmation=args.confirm,
    )
    print("restore=completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
