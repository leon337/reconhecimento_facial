from app.models import Company, Employee, User, Worksite, db
from app.rbac import AccessRole


def _create_account(app, *, username, access_role, company=None, worksite=None, legacy_role=None):
    with app.app_context():
        user = User(
            username=username,
            access_role=access_role,
            role=legacy_role,
            company=company,
            worksite=worksite,
        )
        user.set_password("secret")
        db.session.add(user)
        db.session.commit()
        return user.id


def _login(client, username):
    return client.post(
        "/admin/login",
        data={"username": username, "password": "secret"},
    )


def test_admin_creation_generates_employee_and_account(app, client):
    with app.app_context():
        company = Company(name="Empresa Sintética", slug="empresa-sintetica")
        worksite = Worksite(name="Obra Sintética", company=company)
        admin = User(
            username="admin",
            access_role=AccessRole.ADMIN.value,
            company=company,
            worksite=worksite,
        )
        admin.set_password("secret")
        db.session.add_all([company, worksite, admin])
        db.session.commit()

    assert _login(client, "admin").status_code == 302
    response = client.post(
        "/admin/users",
        data={
            "username": "operador",
            "password": "secret",
            "name": "Pessoa Sintética",
            "registration": "MAT-001",
            "role": "Operador de ponto",
            "access_role": AccessRole.OPERATOR.value,
        },
    )
    assert response.status_code == 302

    with app.app_context():
        account = User.query.filter_by(username="operador").one()
        employee = Employee.query.filter_by(registration="MAT-001").one()
        assert account.employee_id == employee.id
        assert account.company_id == employee.company_id
        assert account.worksite_id == employee.worksite_id
        assert account.access_role == AccessRole.OPERATOR.value


def test_auditor_can_list_but_cannot_create_or_manage_biometrics(app, client):
    with app.app_context():
        auditor = User(username="auditor", access_role=AccessRole.AUDITOR.value)
        auditor.set_password("secret")
        target = User(username="target", access_role=AccessRole.OPERATOR.value)
        target.set_password("secret")
        db.session.add_all([auditor, target])
        db.session.commit()
        target_id = target.id

    assert _login(client, "auditor").status_code == 302
    assert client.get("/admin/users").status_code == 200
    assert client.get("/admin/users/new").status_code == 403
    assert client.post(
        "/admin/users",
        data={"username": "blocked", "password": "secret"},
    ).status_code == 403
    assert client.get(f"/admin/users/{target_id}/biometric").status_code == 403


def test_employee_scope_must_match_account_scope(app):
    with app.app_context():
        company_a = Company(name="Empresa A", slug="empresa-a")
        company_b = Company(name="Empresa B", slug="empresa-b")
        employee = Employee(name="Pessoa Sintética", company=company_a)
        user = User(
            username="cross-scope",
            access_role=AccessRole.OPERATOR.value,
            company=company_b,
            employee=employee,
        )
        user.set_password("secret")
        db.session.add_all([company_a, company_b, employee, user])

        try:
            db.session.commit()
        except ValueError as error:
            db.session.rollback()
            assert str(error) == "user_employee_company_mismatch"
        else:
            raise AssertionError("Vínculo cruzado deveria ser rejeitado")
