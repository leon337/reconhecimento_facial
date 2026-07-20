#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from main import create_app
from app.models import Company, User, Worksite, db
from app.rbac import AccessRole


class BootstrapConfigurationError(RuntimeError):
    pass


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value or value.startswith("CHANGE_ME"):
        raise BootstrapConfigurationError(f"Configure {name} antes de iniciar o piloto.")
    return value


def bootstrap() -> dict[str, str]:
    company_name = required_env("PILOT_COMPANY_NAME")
    company_slug = required_env("PILOT_COMPANY_SLUG")
    worksite_name = required_env("PILOT_WORKSITE_NAME")
    worksite_code = os.environ.get("PILOT_WORKSITE_CODE", "PILOTO-01").strip()
    username = required_env("PILOT_ADMIN_USERNAME")
    password = required_env("PILOT_ADMIN_PASSWORD")
    admin_name = os.environ.get("PILOT_ADMIN_NAME", "Administrador do Piloto").strip()

    if len(password) < 12:
        raise BootstrapConfigurationError("PILOT_ADMIN_PASSWORD deve ter ao menos 12 caracteres.")

    app = create_app({"AUTO_CREATE_SCHEMA": False})
    with app.app_context():
        company = Company.query.filter_by(slug=company_slug).one_or_none()
        if company is None:
            company = Company(name=company_name, slug=company_slug)
            db.session.add(company)
            db.session.flush()
        else:
            company.name = company_name
            company.active = True

        worksite = Worksite.query.filter_by(company_id=company.id, name=worksite_name).one_or_none()
        if worksite is None:
            worksite = Worksite(
                company=company,
                name=worksite_name,
                code=worksite_code or None,
            )
            db.session.add(worksite)
            db.session.flush()
        else:
            worksite.code = worksite_code or worksite.code
            worksite.active = True

        user = User.query.filter_by(username=username).one_or_none()
        created_admin = user is None
        if user is None:
            user = User(
                username=username,
                name=admin_name,
                access_role=AccessRole.SUPER_ADMIN.value,
                role="admin",
                company=company,
                worksite=worksite,
            )
            user.set_password(password)
            db.session.add(user)
        else:
            user.name = admin_name
            user.access_role = AccessRole.SUPER_ADMIN.value
            user.role = "admin"
            user.company = company
            user.worksite = worksite

        db.session.commit()

        return {
            "company": company.slug,
            "worksite": worksite.name,
            "admin": user.username,
            "admin_created": str(created_admin).lower(),
        }


def main() -> int:
    result = bootstrap()
    for key, value in result.items():
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
