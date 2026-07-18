from datetime import datetime, timezone

import pytest

from app.application.use_cases import (
    DuplicateCommandError,
    ExecuteScopedCommand,
    ScopedCommand,
)


class FixedClock:
    def now(self):
        return datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)


class ContextProvider:
    def current_tenant_id(self):
        return "empresa-1"

    def current_worksite_id(self):
        return "obra-7"


class MemoryIdempotency:
    def __init__(self):
        self.keys = set()

    def reserve(self, *, scope, key, expires_at):
        pair = (scope, key)
        if pair in self.keys:
            return False
        self.keys.add(pair)
        return True

    def release(self, *, scope, key):
        self.keys.discard((scope, key))


class MemoryUnitOfWork:
    def __init__(self):
        self.committed = False
        self.rolled_back = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        if exc_type is not None:
            self.rollback()

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


class MemoryAudit:
    def __init__(self):
        self.events = []

    def record(self, **event):
        self.events.append(event)


def build_use_case():
    idempotency = MemoryIdempotency()
    uow = MemoryUnitOfWork()
    audit = MemoryAudit()
    use_case = ExecuteScopedCommand(
        context_provider=ContextProvider(),
        idempotency_store=idempotency,
        clock=FixedClock(),
        unit_of_work=uow,
        audit_sink=audit,
    )
    return use_case, idempotency, uow, audit


def test_executes_command_in_organizational_scope():
    use_case, _, uow, audit = build_use_case()
    command = ScopedCommand(
        idempotency_key="req-1",
        action="employee.synthetic.created",
        actor_id="admin-1",
        subject_id="employee-9",
    )

    result = use_case.execute(command, lambda context: context.scope_key)

    assert result == "tenant:empresa-1:worksite:obra-7"
    assert uow.committed is True
    assert audit.events[0]["tenant_id"] == "empresa-1"
    assert audit.events[0]["metadata"]["worksite_id"] == "obra-7"


def test_rejects_duplicate_command_in_same_scope():
    use_case, _, _, _ = build_use_case()
    command = ScopedCommand(idempotency_key="req-2", action="test.action")

    use_case.execute(command, lambda context: "ok")

    with pytest.raises(DuplicateCommandError):
        use_case.execute(command, lambda context: "duplicado")


def test_releases_idempotency_key_when_operation_fails():
    use_case, idempotency, uow, _ = build_use_case()
    command = ScopedCommand(idempotency_key="req-3", action="test.failure")

    def fail(context):
        raise RuntimeError("falha sintética")

    with pytest.raises(RuntimeError, match="falha sintética"):
        use_case.execute(command, fail)

    assert ("tenant:empresa-1:worksite:obra-7", "req-3") not in idempotency.keys
    assert uow.rolled_back is True


def test_command_requires_non_empty_key_and_action():
    with pytest.raises(ValueError):
        ScopedCommand(idempotency_key=" ", action="valid")

    with pytest.raises(ValueError):
        ScopedCommand(idempotency_key="valid", action=" ")
