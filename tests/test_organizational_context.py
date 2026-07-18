from datetime import datetime, timedelta, timezone

import pytest

from app.application.context import (
    InvalidOrganizationalContext,
    OrganizationalContext,
)
from app.application.contracts import IdempotencyStore, TenantContextProvider


class FakeTenantContextProvider:
    def __init__(self, tenant_id: str, worksite_id: str | None = None):
        self._tenant_id = tenant_id
        self._worksite_id = worksite_id

    def current_tenant_id(self) -> str:
        return self._tenant_id

    def current_worksite_id(self) -> str | None:
        return self._worksite_id


class InMemoryIdempotencyStore:
    def __init__(self):
        self._keys: dict[tuple[str, str], datetime] = {}

    def reserve(self, *, scope: str, key: str, expires_at: datetime) -> bool:
        identity = (scope, key)
        if identity in self._keys:
            return False
        self._keys[identity] = expires_at
        return True

    def release(self, *, scope: str, key: str) -> None:
        self._keys.pop((scope, key), None)


def test_organizational_context_requires_tenant():
    with pytest.raises(InvalidOrganizationalContext):
        OrganizationalContext(tenant_id="   ")


def test_organizational_context_builds_stable_scope_key():
    context = OrganizationalContext(tenant_id="empresa-1", worksite_id="obra-7")
    assert context.scope_key == "tenant:empresa-1:worksite:obra-7"


def test_tenant_provider_satisfies_runtime_protocol():
    provider = FakeTenantContextProvider("empresa-1", "obra-7")
    assert isinstance(provider, TenantContextProvider)


def test_idempotency_store_accepts_only_first_reservation():
    store = InMemoryIdempotencyStore()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    assert isinstance(store, IdempotencyStore)
    assert store.reserve(scope="tenant:empresa-1", key="batida-123", expires_at=expires_at)
    assert not store.reserve(
        scope="tenant:empresa-1", key="batida-123", expires_at=expires_at
    )

    store.release(scope="tenant:empresa-1", key="batida-123")
    assert store.reserve(scope="tenant:empresa-1", key="batida-123", expires_at=expires_at)
