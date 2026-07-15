from sqlalchemy import inspect

from app.models import db


def test_create_app_uses_testing_configuration(app, tmp_path):
    assert app.config["TESTING"] is True
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"
    assert app.config["UPLOAD_FOLDER"].startswith(str(tmp_path))


def test_database_tables_are_created(app):
    with app.app_context():
        table_names = set(inspect(db.engine).get_table_names())

    assert {"users", "pontos"}.issubset(table_names)


def test_admin_user_list_route_responds(client):
    response = client.get("/admin/users")

    assert response.status_code == 200


def test_punch_page_responds(client):
    response = client.get("/punch")

    assert response.status_code == 200
