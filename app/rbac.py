from __future__ import annotations

from enum import StrEnum


class AccessRole(StrEnum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    OPERATOR = "operator"
    AUDITOR = "auditor"


class Permission(StrEnum):
    USERS_VIEW = "users:view"
    USERS_CREATE = "users:create"
    BIOMETRICS_MANAGE = "biometrics:manage"
    PUNCH_VIEW = "punch:view"
    PUNCH_CREATE = "punch:create"


ROLE_PERMISSIONS: dict[AccessRole, frozenset[Permission]] = {
    AccessRole.SUPER_ADMIN: frozenset(Permission),
    AccessRole.ADMIN: frozenset(
        {
            Permission.USERS_VIEW,
            Permission.USERS_CREATE,
            Permission.BIOMETRICS_MANAGE,
            Permission.PUNCH_VIEW,
            Permission.PUNCH_CREATE,
        }
    ),
    AccessRole.MANAGER: frozenset(
        {
            Permission.USERS_VIEW,
            Permission.USERS_CREATE,
            Permission.PUNCH_VIEW,
        }
    ),
    AccessRole.OPERATOR: frozenset({Permission.PUNCH_CREATE}),
    AccessRole.AUDITOR: frozenset({Permission.USERS_VIEW, Permission.PUNCH_VIEW}),
}


def normalize_access_role(value: str | None, *, legacy_role: str | None = None) -> AccessRole | None:
    candidate = value or (AccessRole.ADMIN.value if legacy_role == "admin" else None)
    if candidate is None:
        return None
    try:
        return AccessRole(candidate)
    except ValueError:
        return None


def has_permission(
    access_role: str | None,
    permission: Permission,
    *,
    legacy_role: str | None = None,
) -> bool:
    role = normalize_access_role(access_role, legacy_role=legacy_role)
    return role is not None and permission in ROLE_PERMISSIONS[role]
