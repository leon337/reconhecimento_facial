# app/models.py

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash

from app.rbac import Permission, has_permission


db = SQLAlchemy()


def _resolved_id(entity, relationship_name: str, field_name: str):
    """Resolve uma FK mesmo antes de o SQLAlchemy preencher o campo no flush."""
    value = getattr(entity, field_name)
    if value is not None:
        return value
    related = getattr(entity, relationship_name)
    return related.id if related is not None else None


def _has_relation_or_id(entity, relationship_name: str, field_name: str) -> bool:
    return (
        getattr(entity, relationship_name) is not None
        or getattr(entity, field_name) is not None
    )


def _same_relation(left, right, relationship_name: str, field_name: str) -> bool:
    """Compara escopos persistidos ou objetos ainda sem chave primária."""
    left_related = getattr(left, relationship_name)
    right_related = getattr(right, relationship_name)

    if left_related is not None and right_related is not None:
        if left_related is right_related:
            return True
        left_id = getattr(left_related, "id", None)
        right_id = getattr(right_related, "id", None)
        if left_id is None or right_id is None:
            return False
        return left_id == right_id

    return _resolved_id(left, relationship_name, field_name) == _resolved_id(
        right, relationship_name, field_name
    )


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    active = db.Column(db.Boolean, nullable=False, default=True)

    worksites = db.relationship("Worksite", back_populates="company", lazy=True)
    users = db.relationship("User", back_populates="company", lazy=True)
    employees = db.relationship("Employee", back_populates="company", lazy=True)
    pontos = db.relationship("Ponto", back_populates="company", lazy=True)


class Worksite(db.Model):
    __tablename__ = "worksites"
    __table_args__ = (
        db.UniqueConstraint("company_id", "name", name="uq_worksites_company_name"),
    )

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(
        db.Integer, db.ForeignKey("companies.id"), nullable=False, index=True
    )
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(50), nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True)

    company = db.relationship("Company", back_populates="worksites")
    users = db.relationship("User", back_populates="worksite", lazy=True)
    employees = db.relationship("Employee", back_populates="worksite", lazy=True)
    pontos = db.relationship("Ponto", back_populates="worksite", lazy=True)


class Employee(db.Model):
    """Cadastro funcional separado da credencial de acesso."""

    __tablename__ = "employees"
    __table_args__ = (
        db.UniqueConstraint(
            "company_id", "registration", name="uq_employees_company_registration"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(
        db.Integer, db.ForeignKey("companies.id"), nullable=True, index=True
    )
    worksite_id = db.Column(
        db.Integer, db.ForeignKey("worksites.id"), nullable=True, index=True
    )
    name = db.Column(db.String(120), nullable=False)
    registration = db.Column(db.String(50), nullable=True)
    job_title = db.Column(db.String(80), nullable=True)
    schedule = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    pass_type = db.Column(db.String(50), nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True)

    company = db.relationship("Company", back_populates="employees")
    worksite = db.relationship("Worksite", back_populates="employees")
    user = db.relationship("User", back_populates="employee", uselist=False)

    def validate_organizational_scope(self):
        has_worksite = _has_relation_or_id(self, "worksite", "worksite_id")
        has_company = _has_relation_or_id(self, "company", "company_id")

        if has_worksite and not has_company:
            raise ValueError("worksite_requires_company")
        if self.worksite is not None and not _same_relation(
            self, self.worksite, "company", "company_id"
        ):
            raise ValueError("worksite_company_mismatch")


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    access_role = db.Column(db.String(40), nullable=True, index=True)
    employee_id = db.Column(
        db.Integer, db.ForeignKey("employees.id"), nullable=True, unique=True, index=True
    )

    # Campos legados mantidos temporariamente para compatibilidade.
    name = db.Column(db.String(120), nullable=True)
    registration = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(80), nullable=True)
    schedule = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    pass_type = db.Column(db.String(50), nullable=True)
    face_encoding = db.Column(db.Text, nullable=True)
    photo_url = db.Column(db.String(200), nullable=True)
    company_id = db.Column(
        db.Integer, db.ForeignKey("companies.id"), nullable=True, index=True
    )
    worksite_id = db.Column(
        db.Integer, db.ForeignKey("worksites.id"), nullable=True, index=True
    )

    company = db.relationship("Company", back_populates="users")
    worksite = db.relationship("Worksite", back_populates="users")
    employee = db.relationship("Employee", back_populates="user")
    pontos = db.relationship("Ponto", back_populates="user", lazy=True)

    @classmethod
    def scoped_query(cls, company_id: int, worksite_id: int | None = None):
        query = cls.query.filter_by(company_id=company_id)
        if worksite_id is not None:
            query = query.filter_by(worksite_id=worksite_id)
        return query

    def validate_organizational_scope(self):
        has_worksite = _has_relation_or_id(self, "worksite", "worksite_id")
        has_company = _has_relation_or_id(self, "company", "company_id")

        if has_worksite and not has_company:
            raise ValueError("worksite_requires_company")
        if self.worksite is not None and not _same_relation(
            self, self.worksite, "company", "company_id"
        ):
            raise ValueError("worksite_company_mismatch")
        if self.employee is not None:
            if not _same_relation(self, self.employee, "company", "company_id"):
                raise ValueError("user_employee_company_mismatch")
            if not _same_relation(self, self.employee, "worksite", "worksite_id"):
                raise ValueError("user_employee_worksite_mismatch")

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)

    def can(self, permission: Permission) -> bool:
        return has_permission(
            self.access_role,
            permission,
            legacy_role=self.role,
        )


class Ponto(db.Model):
    __tablename__ = "pontos"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    company_id = db.Column(
        db.Integer, db.ForeignKey("companies.id"), nullable=True, index=True
    )
    worksite_id = db.Column(
        db.Integer, db.ForeignKey("worksites.id"), nullable=True, index=True
    )
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    tipo = db.Column(db.String(10), nullable=False)

    user = db.relationship("User", back_populates="pontos")
    company = db.relationship("Company", back_populates="pontos")
    worksite = db.relationship("Worksite", back_populates="pontos")

    @classmethod
    def scoped_query(cls, company_id: int, worksite_id: int | None = None):
        query = cls.query.filter_by(company_id=company_id)
        if worksite_id is not None:
            query = query.filter_by(worksite_id=worksite_id)
        return query

    @classmethod
    def from_user(cls, user: User, *, tipo: str, timestamp=None):
        return cls(
            user_id=user.id,
            company_id=user.company_id,
            worksite_id=user.worksite_id,
            tipo=tipo,
            timestamp=timestamp or datetime.utcnow(),
        )

    def validate_organizational_scope(self):
        has_worksite = _has_relation_or_id(self, "worksite", "worksite_id")
        has_company = _has_relation_or_id(self, "company", "company_id")

        if has_worksite and not has_company:
            raise ValueError("worksite_requires_company")
        if self.worksite is not None and not _same_relation(
            self, self.worksite, "company", "company_id"
        ):
            raise ValueError("worksite_company_mismatch")
        if self.user is not None:
            if not _same_relation(self, self.user, "company", "company_id"):
                raise ValueError("ponto_user_company_mismatch")
            if not _same_relation(self, self.user, "worksite", "worksite_id"):
                raise ValueError("ponto_user_worksite_mismatch")


@event.listens_for(Session, "before_flush")
def validate_organizational_scope_before_flush(session, flush_context, instances):
    for entity in session.new.union(session.dirty):
        if isinstance(entity, (Employee, User, Ponto)):
            entity.validate_organizational_scope()
