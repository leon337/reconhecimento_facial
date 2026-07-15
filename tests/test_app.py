from sqlalchemy import inspect

from app.models import User, db


def create_admin(app, username="admin", password="senha-segura"):
    with app.app_context():
        user = User(username=username, role="admin")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()


def login_admin(client, username="admin", password="senha-segura"):
    return client.post(
        "/admin/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )


def test_create_app_uses_testing_configuration(app, tmp_path):
    assert app.config["TESTING"] is True
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"
    assert app.config["UPLOAD_FOLDER"].startswith(str(tmp_path))


def test_database_tables_are_created(app):
    with app.app_context():
        table_names = set(inspect(db.engine).get_table_names())

    assert {"users", "pontos"}.issubset(table_names)


def test_admin_user_list_requires_login(client):
    response = client.get("/admin/users")

    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"]


def test_admin_login_rejects_invalid_credentials(client):
    response = login_admin(client, password="incorreta")

    assert response.status_code == 401
    assert b"Credenciais administrativas inv" in response.data


def test_admin_login_allows_admin_and_protected_route(app, client):
    create_admin(app)

    login_response = login_admin(client)
    users_response = client.get("/admin/users")

    assert login_response.status_code == 302
    assert login_response.headers["Location"].endswith("/admin/users")
    assert users_response.status_code == 200


def test_non_admin_user_cannot_access_admin_routes(app, client):
    with app.app_context():
        user = User(username="funcionario", role="funcionario")
        user.set_password("senha-segura")
        db.session.add(user)
        db.session.commit()

    response = login_admin(client, username="funcionario")

    assert response.status_code == 401


def test_admin_logout_clears_session(app, client):
    create_admin(app)
    login_admin(client)

    logout_response = client.post("/admin/logout")
    protected_response = client.get("/admin/users")

    assert logout_response.status_code == 302
    assert logout_response.headers["Location"].endswith("/admin/login")
    assert protected_response.status_code == 302


def test_punch_page_remains_public(client):
    response = client.get("/punch")
    assert response.status_code == 200
