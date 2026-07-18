import json

import numpy as np

from app.models import Company, Ponto, User, Worksite, db
from app.punch import service


def _user(username, company, worksite):
    user = User(
        username=username,
        password_hash="test-hash",
        company=company,
        worksite=worksite,
    )
    db.session.add(user)
    return user


def test_users_and_pontos_are_scoped_by_company_and_worksite(app):
    with app.app_context():
        company_a = Company(name="Potiguar", slug="potiguar")
        company_b = Company(name="Outra", slug="outra")
        worksite_a = Worksite(name="Obra A", company=company_a)
        worksite_b = Worksite(name="Obra B", company=company_b)
        user_a = _user("leo-a", company_a, worksite_a)
        user_b = _user("leo-b", company_b, worksite_b)
        db.session.flush()

        db.session.add_all(
            [
                Ponto.from_user(user_a, tipo="ENTRADA"),
                Ponto.from_user(user_b, tipo="ENTRADA"),
            ]
        )
        db.session.commit()

        assert User.scoped_query(company_a.id).all() == [user_a]
        assert User.scoped_query(company_b.id, worksite_b.id).all() == [user_b]
        assert Ponto.scoped_query(company_a.id, worksite_a.id).one().user == user_a
        assert Ponto.scoped_query(company_b.id).one().user == user_b


def test_ponto_inherits_organizational_scope_from_user(app):
    with app.app_context():
        company = Company(name="Potiguar", slug="potiguar")
        worksite = Worksite(name="Barricadas", company=company)
        user = _user("leo", company, worksite)
        db.session.flush()

        ponto = Ponto.from_user(user, tipo="SAÍDA")

        assert ponto.company_id == company.id
        assert ponto.worksite_id == worksite.id
        assert ponto.user_id == user.id


def test_recognition_rejects_worksite_without_company_scope(app, monkeypatch):
    monkeypatch.setattr(service.face_recognition, "load_image_file", lambda _: object())
    monkeypatch.setattr(
        service.face_recognition,
        "face_encodings",
        lambda _: [np.zeros(128)],
    )

    with app.app_context():
        result = service.recognize_registered_user(object(), worksite_id=10)

    assert result.user is None
    assert result.reason == "company_scope_required"


def test_recognition_only_compares_users_from_requested_company(app, monkeypatch):
    monkeypatch.setattr(service.face_recognition, "load_image_file", lambda _: object())
    monkeypatch.setattr(
        service.face_recognition,
        "face_encodings",
        lambda _: [np.zeros(128)],
    )
    monkeypatch.setattr(
        service.face_recognition,
        "face_distance",
        lambda known, unknown: np.asarray([0.0 for _ in known]),
    )

    with app.app_context():
        company_a = Company(name="Potiguar", slug="potiguar")
        company_b = Company(name="Outra", slug="outra")
        worksite_a = Worksite(name="Obra A", company=company_a)
        worksite_b = Worksite(name="Obra B", company=company_b)
        user_a = _user("leo-a", company_a, worksite_a)
        user_b = _user("leo-b", company_b, worksite_b)
        user_a.face_encoding = json.dumps([0.0] * 128)
        user_b.face_encoding = json.dumps([0.0] * 128)
        db.session.commit()

        result = service.recognize_registered_user(
            object(), company_id=company_b.id, worksite_id=worksite_b.id
        )

        assert result.user == user_b
        assert result.user != user_a
        assert result.reason == "matched"
