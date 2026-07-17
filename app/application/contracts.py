"""Contratos arquiteturais da camada de aplicação.

Os Protocols permitem que os casos de uso dependam de abstrações testáveis,
sem importar implementações concretas de Flask, SQLAlchemy ou filesystem.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, Protocol, TypeVar, runtime_checkable

EntityT = TypeVar("EntityT")
IdT = TypeVar("IdT")


@runtime_checkable
class Clock(Protocol):
    """Fonte de tempo injetável e timezone-aware."""

    def now(self) -> datetime:
        """Retorna o instante atual com informação explícita de timezone."""


@runtime_checkable
class Repository(Protocol[EntityT, IdT]):
    """Contrato mínimo para repositórios de entidades."""

    def get(self, entity_id: IdT) -> EntityT | None:
        """Busca uma entidade pelo identificador."""

    def add(self, entity: EntityT) -> None:
        """Agenda a inclusão de uma entidade."""

    def list(self, **filters: Any) -> Iterable[EntityT]:
        """Lista entidades respeitando filtros e escopo organizacional."""


@runtime_checkable
class UnitOfWork(Protocol):
    """Delimita uma transação de aplicação."""

    def __enter__(self) -> UnitOfWork:
        """Abre o contexto transacional."""

    def __exit__(self, exc_type, exc, traceback) -> None:
        """Finaliza o contexto, realizando rollback em caso de erro."""

    def commit(self) -> None:
        """Confirma a transação atual."""

    def rollback(self) -> None:
        """Desfaz a transação atual."""


@runtime_checkable
class ObjectStorage(Protocol):
    """Armazena artefatos privados fora da pasta pública da aplicação."""

    def save_private(self, *, content: bytes, media_type: str) -> str:
        """Persiste conteúdo privado e retorna uma chave opaca."""

    def read_private(self, key: str) -> bytes:
        """Lê conteúdo privado mediante autorização externa."""

    def delete_private(self, key: str) -> None:
        """Remove conteúdo privado conforme política de retenção."""


@runtime_checkable
class SecretBox(Protocol):
    """Criptografa e descriptografa dados sensíveis em repouso."""

    def encrypt(self, plaintext: bytes, *, context: bytes = b"") -> bytes:
        """Criptografa dados vinculando-os a um contexto opcional."""

    def decrypt(self, ciphertext: bytes, *, context: bytes = b"") -> bytes:
        """Descriptografa dados validando o mesmo contexto."""


@runtime_checkable
class AuditSink(Protocol):
    """Registra eventos imutáveis de auditoria."""

    def record(
        self,
        *,
        action: str,
        actor_id: str | None,
        tenant_id: str | None,
        subject_id: str | None,
        occurred_at: datetime,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Registra um evento sem expor dados biométricos em texto aberto."""
