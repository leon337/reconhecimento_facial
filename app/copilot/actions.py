"""Escrita estritamente autorizada de cadastro iniciado pelo Copiloto.

O modelo pode *sugerir* um rascunho, mas a criação só ocorre com clique
confirmatório em formulário próprio e segundo controle de permissão do Flask.
Não há funções de biometria ou ponto neste módulo.
"""
from __future__ import annotations

import re
import secrets
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.models import Employee, User, db
from app.observability import audit
from app.rbac import AccessRole


USERNAME_RE = re.compile(r"^[a-z][a-z0-9._-]{2,63}$")
FIELDS = frozenset({
    "request_id", "name", "username", "registration", "job_title", "schedule",
})


@dataclass(frozen=True)
class EmployeeDraft:
    request_id: str
    name: str
    username: str
    registration: str | None
    job_title: str | None
    schedule: str | None


class InvalidDraft(ValueError):
    pass


class DuplicateEmployee(RuntimeError):
    pass


def validate_draft(body: object) -> EmployeeDraft:
    if not isinstance(body, dict) or set(body) - FIELDS:
        raise InvalidDraft("Campos não reconhecidos no cadastro.")
    request_id = body.get("request_id")
    try:
        if not isinstance(request_id, str) or str(UUID(request_id)) != request_id:
            raise ValueError
    except ValueError as exc:
        raise InvalidDraft("Identificador de confirmação inválido.") from exc
    for key in ("name", "username", "registration", "job_title", "schedule"):
        if key in body and not isinstance(body[key], str):
            raise InvalidDraft("Campos precisam ser textos.")
    name = (body.get("name") or "").strip()
    username = (body.get("username") or "").strip().lower()
    if not 3 <= len(name) <= 120 or "<" in name or ">" in name:
        raise InvalidDraft("Informe o nome completo, com até 120 caracteres.")
    if not USERNAME_RE.fullmatch(username):
        raise InvalidDraft("Usuário deve ter 3 a 64 caracteres: letras sem acento, números, ponto, hífen ou sublinhado.")
    options = {}
    for key, maximum in (("registration", 50), ("job_title", 80), ("schedule", 120)):
        value = (body.get(key) or "").strip()
        if len(value) > maximum or any(ord(c) < 32 for c in value):
            raise InvalidDraft("Um campo adicional tem tamanho ou caracteres inválidos.")
        options[key] = value or None
    return EmployeeDraft(request_id, name, username, **options)


def create_employee(draft: EmployeeDraft, *, actor, company_id, worksite_id) -> tuple[User, str]:
    """Executa transação + auditoria. Nunca envia credencial a modelo ou log."""
    # Consulta preventiva melhora a mensagem; UNIQUE do banco encerra corridas.
    if User.query.filter_by(username=draft.username).first() is not None:
        raise DuplicateEmployee("Esse usuário já existe.")
    if draft.registration and Employee.query.filter_by(
        company_id=company_id, registration=draft.registration
    ).first() is not None:
        raise DuplicateEmployee("Essa matrícula já está cadastrada.")

    # Senha criada somente na confirmação humana; o Gemini nunca a conhece.
    temporary_password = secrets.token_urlsafe(21)
    employee = Employee(
        name=draft.name,
        registration=draft.registration,
        job_title=draft.job_title,
        schedule=draft.schedule,
        company_id=company_id,
        worksite_id=worksite_id,
    )
    user = User(
        username=draft.username,
        access_role=AccessRole.OPERATOR.value,
        employee=employee,
        name=draft.name,
        registration=draft.registration,
        role=draft.job_title,
        schedule=draft.schedule,
        company_id=company_id,
        worksite_id=worksite_id,
    )
    user.set_password(temporary_password)
    try:
        db.session.add_all([employee, user])
        db.session.flush()
        audit(
            "copilot.employee.create", "success",
            actor=actor, target_type="user", target_id=user.id,
            metadata={"source": "human_confirmed", "request_id":draft.request_id},
        )
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise DuplicateEmployee("Cadastro duplicado ou conflito de matrícula.") from exc
    except Exception:
        db.session.rollback()
        raise
    return user, temporary_password
