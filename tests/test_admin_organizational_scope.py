from app.models import Company, User, Worksite, db


def _create_user(username, password, role, company=None, worksite=None):
    user = User(
        username=username,
        role=role,
        company=company,
        worksite=worksite,
    )
    user.set_password(password)
    db.session.add(user)
    return user


def _login(client, username="admin-a", password="secret"):
    return client.post(
        "/admin/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )


def test_admin_list_only_shows_users_from_its_company_and_worksite(app, client):
    with app.app_context():
        company_a = Company(name="Potiguar", slug="potiguar")
        company_b = Company(name="Outra", slug="outra")
        worksite_a = Worksite(name="Obra A", company=company_a)
        worksite_b = Worksite(name="Obra B", company=company_b)
        _create_user("admin-a", "secret", "admin", company_a, worksite_a)
        _create_user("funcionario-a", "secret", "employee", company_a, worksite_a)
        _create_user("funcionario-b", "secret", "employee", company_b, worksite_b)
        db.session.commit()

    response = _login(client)
    assert response.status_code == 302

    response = client.get("/admin/users")
    assert response.status_code == 200
    assert b"funcionario-a" in response.data
    assert b"funcionario-b" not in response.data


def test_admin_created_user_inherits_session_scope(app, client):
    with app.app_context():
        company = Company(name="Potiguar", slug="potiguar")
        worksite = Worksite(name="Barricadas", company=company)
        _create_user("admin-a", "secret", "admin", company, worksite)
        db.session.commit()
        company_id = company.id
        worksite_id = worksite.id

    _login(client)
    response = client.post(
        "/admin/users",
        data={
            "username": "novo-funcionario",
            "password": "secret",
            "name": "Novo Funcionário",
            "role": "employee",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    with app.app_context():
        user = User.query.filter_by(username="novo-funcionario").one()
        assert user.company_id == company_id
        assert user.worksite_id == worksite_id


def test_admin_cannot_access_biometric_page_from_another_company(app, client):
    with app.app_context():
        company_a = Company(name="Potiguar", slug="potiguar")
        company_b = Company(name="Outra", slug="outra")
        worksite_a = Worksite(name="Obra A", company=company_a)
        worksite_b = Worksite(name="Obra B", company=company_b)
        _create_user("admin-a", "secret", "admin", company_a, worksite_a)
        foreign_user = _create_user(
            "funcionario-b", "secret", "employee", company_b, worksite_b
        )
        db.session.commit()
        foreign_user_id = foreign_user.id

    _login(client)
    response = client.get(f"/admin/users/{foreign_user_id}/biometric")

    assert response.status_code == 404


def test_legacy_admin_without_scope_keeps_existing_behavior(app, client):
    with app.app_context():
        _create_user("legacy-admin", "secret", "admin")
        _create_user("legacy-user", "secret", "employee")
        db.session.commit()

    response = _login(client, username="legacy-admin")
    assert response.status_code == 302

    response = client.get("/admin/users")
    assert response.status_code == 200
    assert b"legacy-user" in response.data
