from app.rbac import AccessRole, Permission, has_permission, normalize_access_role


def test_admin_has_all_operational_permissions():
    assert has_permission(AccessRole.ADMIN.value, Permission.USERS_VIEW)
    assert has_permission(AccessRole.ADMIN.value, Permission.USERS_CREATE)
    assert has_permission(AccessRole.ADMIN.value, Permission.BIOMETRICS_MANAGE)


def test_auditor_is_read_only():
    assert has_permission(AccessRole.AUDITOR.value, Permission.USERS_VIEW)
    assert not has_permission(AccessRole.AUDITOR.value, Permission.USERS_CREATE)
    assert not has_permission(AccessRole.AUDITOR.value, Permission.BIOMETRICS_MANAGE)


def test_legacy_admin_role_is_normalized_during_transition():
    assert normalize_access_role(None, legacy_role="admin") == AccessRole.ADMIN
    assert has_permission(None, Permission.USERS_VIEW, legacy_role="admin")


def test_unknown_role_has_no_permissions():
    assert normalize_access_role("unknown") is None
    assert not has_permission("unknown", Permission.USERS_VIEW)
