"""O Gemini prepara dados, mas só o administrador pode confirmar e gravar."""
from uuid import uuid4

from app.models import Employee, User, db
from app.rbac import AccessRole


def login(app, client, role):
    username = "copilot-create-" + role
    with app.app_context():
        user = User(username=username, access_role=role)
        user.set_password("senha-sintetica")
        db.session.add(user)
        db.session.commit()
    assert client.post("/admin/login", data={
        "username": username, "password": "senha-sintetica"
    }).status_code == 302


def body(**values):
    return dict(
        request_id=str(uuid4()),
        name="Maria de Teste",
        username="maria.teste",
        registration="SYN-101",
        job_title="Atendente",
        schedule="08:00-17:00",
        **values,
    )


def test_feature_disabled_prevents_writes(app, client):
    login(app, client, AccessRole.ADMIN.value)
    assert client.post("/admin/copilot/employee-create", json=body()).status_code == 503
    with app.app_context():
        assert User.query.filter_by(username="maria.teste").count() == 0


def test_operator_cannot_create_and_auditor_forbidden(app, client):
    login(app, client, AccessRole.AUDITOR.value)
    app.config.update(COPILOT_ENABLED=True, COPILOT_ACTIONS_ENABLED=True)
    assert client.post("/admin/copilot/employee-create", json=body()).status_code == 403
    with app.app_context():
        assert User.query.filter_by(username="maria.teste").count() == 0


def test_confirmed_creation_audits_and_generates_password_once(app, client):
    login(app, client, AccessRole.ADMIN.value)
    app.config.update(COPILOT_ENABLED=True, COPILOT_ACTIONS_ENABLED=True)
    draft = body()
    response = client.post("/admin/copilot/employee-create", json=draft)
    assert response.status_code == 201
    result = response.get_json()
    assert result["username"] == draft["username"]
    assert len(result["temporary_password"]) >= 20
    assert response.headers["Cache-Control"].startswith("no-store")
    with app.app_context():
        user = User.query.filter_by(username=draft["username"]).one()
        assert user.access_role == AccessRole.OPERATOR.value
        assert user.check_password(result["temporary_password"])
        assert user.employee.name == draft["name"]
        assert user.employee.registration == draft["registration"]
        from app.audit_models import AuditEvent
        assert AuditEvent.query.filter_by(action="copilot.employee.create").count() == 1
    replay = client.post("/admin/copilot/employee-create", json=draft)
    assert replay.status_code == 409
    assert "temporary_password" not in replay.get_data(as_text=True)
    with app.app_context():
        assert User.query.filter_by(username=draft["username"]).count() == 1


def test_no_unapproved_fields_or_invalid_payload(app, client):
    login(app, client, AccessRole.ADMIN.value)
    app.config.update(COPILOT_ENABLED=True, COPILOT_ACTIONS_ENABLED=True)
    for item in (
        {"request_id":str(uuid4()), "name":"Maria", "username":"maria.teste","access_role":"admin"},
        {"request_id":str(uuid4()), "name":"Maria", "username":"maria.teste","company_id":999},
        {"request_id":str(uuid4()), "name":"Maria", "username":"Maria Teste"},
        {"request_id":str(uuid4()), "name":"M", "username":"maria.teste"},
        {"request_id":"not-uuid", "name":"Maria de Teste", "username":"maria.teste"},
    ):
        assert client.post("/admin/copilot/employee-create", json=item).status_code == 400
    with app.app_context():
        assert Employee.query.count() == 0


def test_guests_cannot_create(client):
    assert client.post("/admin/copilot/employee-create", json=body()).status_code == 302


def test_demo_only_allows_synthetic_records(app, client, monkeypatch):
    login(app, client, AccessRole.ADMIN.value)
    app.config.update(COPILOT_ENABLED=True, COPILOT_ACTIONS_ENABLED=True)
    monkeypatch.setenv("POTIGUAR_COPILOT_DEMO_DAILY_LIMIT", "12")
    from uuid import uuid4
    real_data = {
        "request_id": str(uuid4()),
        "name": "Maria da Silva", "username": "maria.silva",
        "registration": "CPF123",
    }
    result = client.post("/admin/copilot/employee-create", json=real_data)
    assert result.status_code == 400
    with app.app_context():
        assert User.query.filter_by(username="maria.silva").count() == 0

def test_copilot_respects_organizational_scope(app, client):
    from app.models import Company, Worksite
    with app.app_context():
        company = Company(name="Companhia Sintética", slug="synthetic-actions-001")
        worksite = Worksite(name="Obra Sintética", company=company)
        manager = User(
            username="manager-scoped",
            access_role=AccessRole.MANAGER.value,
            company=company,
            worksite=worksite,
        )
        manager.set_password("senha-sintetica")
        db.session.add_all([company, worksite, manager])
        db.session.commit()
        company_id, worksite_id = company.id, worksite.id
    assert client.post("/admin/login", data={
        "username":"manager-scoped", "password":"senha-sintetica"
    }).status_code == 302
    app.config.update(COPILOT_ENABLED=True, COPILOT_ACTIONS_ENABLED=True)
    response=client.post("/admin/copilot/employee-create", json={
        "request_id":str(uuid4()), "name":"Teste de Escopo",
        "username":"escopo.teste", "registration":"TEST-SCOPE-001",
    })
    assert response.status_code==201
    with app.app_context():
        created = User.query.filter_by(username="escopo.teste").one()
        assert created.company_id==company_id
        assert created.worksite_id==worksite_id
        assert created.employee.company_id==company_id
        assert created.employee.worksite_id==worksite_id
        assert created.access_role==AccessRole.OPERATOR.value
