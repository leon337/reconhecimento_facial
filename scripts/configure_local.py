#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import secrets
from pathlib import Path


def token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def fernet_key() -> str:
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("ascii")


def render_env(admin_username: str, company_name: str, worksite_name: str) -> tuple[str, str]:
    admin_password = token(18)
    values = {
        "APP_ENV": "pilot",
        "SECRET_KEY": token(48),
        "BIOMETRIC_ENCRYPTION_KEY": fernet_key(),
        "POSTGRES_DB": "controle_ponto_piloto",
        "POSTGRES_USER": "controle_ponto",
        "POSTGRES_PASSWORD": token(24),
        "PILOT_COMPANY_NAME": company_name,
        "PILOT_COMPANY_SLUG": "potiguar",
        "PILOT_WORKSITE_NAME": worksite_name,
        "PILOT_WORKSITE_CODE": "PILOTO-01",
        "PILOT_ADMIN_USERNAME": admin_username,
        "PILOT_ADMIN_PASSWORD": admin_password,
        "PILOT_ADMIN_NAME": "Administrador do Piloto",
        "WEB_CONCURRENCY": "2",
    }
    content = "\n".join(f"{key}={value}" for key, value in values.items()) + "\n"
    return content, admin_password


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera .env.local seguro para o piloto.")
    parser.add_argument("--output", type=Path, default=Path(".env.local"))
    parser.add_argument("--admin", default="admin")
    parser.add_argument("--company", default="Potiguar")
    parser.add_argument("--worksite", default="Obra Piloto")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.output.exists() and not args.force:
        raise SystemExit(f"{args.output} já existe. Use --force apenas para substituir conscientemente.")

    content, admin_password = render_env(args.admin, args.company, args.worksite)
    args.output.write_text(content, encoding="utf-8")
    try:
        args.output.chmod(0o600)
    except OSError:
        pass

    print(f"config_file={args.output}")
    print(f"admin_username={args.admin}")
    print(f"admin_password={admin_password}")
    print("Guarde a senha. O arquivo .env.local não deve ser enviado ao GitHub.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
