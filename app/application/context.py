from __future__ import annotations

from dataclasses import dataclass


class InvalidOrganizationalContext(ValueError):
    pass


@dataclass(frozen=True)
class OrganizationalContext:
    tenant_id: str
    worksite_id: str | None = None

    def __post_init__(self) -> None:
        tenant_id = self.tenant_id.strip()
        if not tenant_id:
            raise InvalidOrganizationalContext("tenant_id é obrigatório.")
        object.__setattr__(self, "tenant_id", tenant_id)

        if self.worksite_id is not None:
            worksite_id = self.worksite_id.strip()
            if not worksite_id:
                raise InvalidOrganizationalContext(
                    "worksite_id não pode ser vazio quando informado."
                )
            object.__setattr__(self, "worksite_id", worksite_id)

    @property
    def scope_key(self) -> str:
        return (
            f"tenant:{self.tenant_id}:worksite:{self.worksite_id}"
            if self.worksite_id
            else f"tenant:{self.tenant_id}"
        )
