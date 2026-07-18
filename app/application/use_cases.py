"""Casos de uso mínimos da fundação arquitetural.

Este módulo não conhece Flask, SQLAlchemy ou o filesystem. As dependências
externas entram por contratos definidos em ``app.application.contracts``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any, Callable, Generic, TypeVar

from app.application.context import OrganizationalContext
from app.application.contracts import (
    AuditSink,
    Clock,
    IdempotencyStore,
    TenantContextProvider,
    UnitOfWork,
)

ResultT = TypeVar("ResultT")


class DuplicateCommandError(RuntimeError):
    """Indica que a mesma operação já foi reservada no mesmo escopo."""


@dataclass(frozen=True)
class ScopedCommand:
    """Dados comuns a comandos mutáveis executados sob empresa/obra."""

    idempotency_key: str
    action: str
    actor_id: str | None = None
    subject_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.idempotency_key.strip():
            raise ValueError("A chave de idempotência não pode estar vazia.")
        if not self.action.strip():
            raise ValueError("A ação não pode estar vazia.")


class ExecuteScopedCommand(Generic[ResultT]):
    """Executa uma operação mutável com escopo, transação e idempotência.

    A implementação concreta do ``AuditSink`` deverá participar da mesma
    transação quando a FASE 9.1 introduzir persistência real.
    """

    def __init__(
        self,
        *,
        context_provider: TenantContextProvider,
        idempotency_store: IdempotencyStore,
        clock: Clock,
        unit_of_work: UnitOfWork,
        audit_sink: AuditSink,
        reservation_ttl: timedelta = timedelta(minutes=5),
    ) -> None:
        if reservation_ttl <= timedelta(0):
            raise ValueError("O TTL de idempotência deve ser positivo.")
        self._context_provider = context_provider
        self._idempotency_store = idempotency_store
        self._clock = clock
        self._unit_of_work = unit_of_work
        self._audit_sink = audit_sink
        self._reservation_ttl = reservation_ttl

    def execute(
        self,
        command: ScopedCommand,
        operation: Callable[[OrganizationalContext], ResultT],
    ) -> ResultT:
        context = OrganizationalContext(
            tenant_id=self._context_provider.current_tenant_id(),
            worksite_id=self._context_provider.current_worksite_id(),
        )
        now = self._clock.now()
        scope = context.scope_key
        reserved = self._idempotency_store.reserve(
            scope=scope,
            key=command.idempotency_key,
            expires_at=now + self._reservation_ttl,
        )
        if not reserved:
            raise DuplicateCommandError(
                f"Operação duplicada no escopo {scope!r}."
            )

        try:
            with self._unit_of_work as uow:
                result = operation(context)
                self._audit_sink.record(
                    action=command.action,
                    actor_id=command.actor_id,
                    tenant_id=context.tenant_id,
                    subject_id=command.subject_id,
                    occurred_at=now,
                    metadata={
                        **command.metadata,
                        "worksite_id": context.worksite_id,
                        "idempotency_key": command.idempotency_key,
                    },
                )
                uow.commit()
                return result
        except Exception:
            self._idempotency_store.release(
                scope=scope,
                key=command.idempotency_key,
            )
            raise
