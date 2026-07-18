from datetime import datetime
from io import BytesIO

from app.models import Ponto, User, db
from app.punch.rules import check_duplicate_punch
from app.punch.service import RecognitionResult


def create_employee(app):
    with app.app_context():
        user = User(username="funcionario", name="Funcionário Teste", role="funcionario")
        user.set_password("senha-teste")
        db.session.add(user)
        db.session.commit()
        return user.id


def test_punch_post_requires_image(client):
    response = client.post("/punch", data={"tipo": "ENTRADA"})

    assert response.status_code == 400
    assert response.get_json()["status"] == "error"


def test_punch_post_rejects_invalid_type(client):
    response = client.post(
        "/punch",
        data={"tipo": "INTERVALO", "image": (BytesIO(b"imagem"), "captura.jpg")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "Tipo de ponto inválido."


def test_punch_post_returns_recognition_error(client, monkeypatch):
    monkeypatch.setattr(
        "app.punch.routes.recognize_registered_user",
        lambda image, tolerance, company_id=None, worksite_id=None: RecognitionResult(
            None, "unknown_face"
        ),
    )
    response = client.post(
        "/punch",
        data={"tipo": "ENTRADA", "image": (BytesIO(b"imagem"), "captura.jpg")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 422
    assert response.get_json()["code"] == "unknown_face"


def test_punch_post_records_recognized_user(app, client, monkeypatch):
    user_id = create_employee(app)

    def recognize(image, tolerance, company_id=None, worksite_id=None):
        with app.app_context():
            return RecognitionResult(db.session.get(User, user_id), "matched")

    monkeypatch.setattr("app.punch.routes.recognize_registered_user", recognize)

    response = client.post(
        "/punch",
        data={"tipo": "ENTRADA", "image": (BytesIO(b"imagem"), "captura.jpg")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 201
    assert response.get_json()["user"]["id"] == user_id

    with app.app_context():
        records = Ponto.query.filter_by(user_id=user_id).all()
        assert len(records) == 1
        assert records[0].tipo == "ENTRADA"


def test_duplicate_rule_blocks_recent_punch(app):
    user_id = create_employee(app)
    now = datetime(2026, 7, 15, 12, 0, 30)

    with app.app_context():
        db.session.add(
            Ponto(
                user_id=user_id,
                tipo="ENTRADA",
                timestamp=datetime(2026, 7, 15, 12, 0, 0),
            )
        )
        db.session.commit()

        result = check_duplicate_punch(user_id, now=now, window_seconds=60)

    assert result.blocked is True
    assert result.retry_after_seconds == 30


def test_duplicate_rule_allows_punch_after_window(app):
    user_id = create_employee(app)
    now = datetime(2026, 7, 15, 12, 2, 0)

    with app.app_context():
        db.session.add(
            Ponto(
                user_id=user_id,
                tipo="ENTRADA",
                timestamp=datetime(2026, 7, 15, 12, 0, 0),
            )
        )
        db.session.commit()

        result = check_duplicate_punch(user_id, now=now, window_seconds=60)

    assert result.blocked is False
    assert result.retry_after_seconds == 0


def test_punch_post_rejects_duplicate_record(app, client, monkeypatch):
    user_id = create_employee(app)

    with app.app_context():
        db.session.add(
            Ponto(
                user_id=user_id,
                tipo="ENTRADA",
                timestamp=datetime.utcnow(),
            )
        )
        db.session.commit()

    def recognize(image, tolerance, company_id=None, worksite_id=None):
        with app.app_context():
            return RecognitionResult(db.session.get(User, user_id), "matched")

    monkeypatch.setattr("app.punch.routes.recognize_registered_user", recognize)

    response = client.post(
        "/punch",
        data={"tipo": "SAIDA", "image": (BytesIO(b"imagem"), "captura.jpg")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 409
    payload = response.get_json()
    assert payload["code"] == "duplicate_punch"
    assert payload["retry_after_seconds"] >= 1

    with app.app_context():
        assert Ponto.query.filter_by(user_id=user_id).count() == 1
