"""Adaptadores temporários para a persistência legada.

Eles permitem introduzir casos de uso por contratos sem reescrever imediatamente
as rotas e os modelos existentes. Devem ser substituídos gradualmente após as
migrations da FASE 9.1.
"""

from __future__ import annotations

from typing import Any, Iterable

from app.models import User, db


class LegacyUserRepository:
    """Adapta o modelo ``User`` atual ao contrato básico de repositório."""

    def get(self, entity_id: int) -> User | None:
        return db.session.get(User, entity_id)

    def add(self, entity: User) -> None:
        db.session.add(entity)

    def list(self, **filters: Any) -> Iterable[User]:
        allowed = {
            "username",
            "registration",
            "role",
        }
        unsupported = set(filters) - allowed
        if unsupported:
            names = ", ".join(sorted(unsupported))
            raise ValueError(f"Filtros legados não suportados: {names}.")
        return User.query.filter_by(**filters).all()


class LegacySqlAlchemyUnitOfWork:
    """Delimita commit e rollback usando a sessão SQLAlchemy atual."""

    def __enter__(self) -> "LegacySqlAlchemyUnitOfWork":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        if exc_type is not None:
            self.rollback()

    def commit(self) -> None:
        db.session.commit()

    def rollback(self) -> None:
        db.session.rollback()
