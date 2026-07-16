from io import BytesIO

from app.models import Ponto, User, db
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
        lambda image, tolerance: RecognitionResult(None, "unknown_face"),
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

    def recognize(image, tolerance):
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
