# app/models.py

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    active = db.Column(db.Boolean, nullable=False, default=True)

    worksites = db.relationship("Worksite", back_populates="company", lazy=True)
    users = db.relationship("User", back_populates="company", lazy=True)
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
    pontos = db.relationship("Ponto", back_populates="worksite", lazy=True)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
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
    pontos = db.relationship("Ponto", back_populates="user", lazy=True)

    @classmethod
    def scoped_query(cls, company_id: int, worksite_id: int | None = None):
        query = cls.query.filter_by(company_id=company_id)
        if worksite_id is not None:
            query = query.filter_by(worksite_id=worksite_id)
        return query

    def validate_organizational_scope(self):
        if self.worksite is None and self.worksite_id is None:
            return
        if self.company is None and self.company_id is None:
            raise ValueError("worksite_requires_company")

        worksite_company_id = (
            self.worksite.company_id if self.worksite is not None else None
        )
        company_id = self.company_id or (self.company.id if self.company is not None else None)
        if worksite_company_id is not None and company_id != worksite_company_id:
            raise ValueError("worksite_company_mismatch")

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)


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
        if self.worksite_id is not None and self.company_id is None:
            raise ValueError("worksite_requires_company")

        if self.worksite is not None:
            worksite_company_id = self.worksite.company_id
            if worksite_company_id is not None and self.company_id != worksite_company_id:
                raise ValueError("worksite_company_mismatch")

        if self.user is not None:
            if self.company_id != self.user.company_id:
                raise ValueError("ponto_user_company_mismatch")
            if self.worksite_id != self.user.worksite_id:
                raise ValueError("ponto_user_worksite_mismatch")


@event.listens_for(Session, "before_flush")
def validate_organizational_scope_before_flush(session, flush_context, instances):
    for entity in session.new.union(session.dirty):
        if isinstance(entity, (User, Ponto)):
            entity.validate_organizational_scope()
