from app.models import Company, User, Worksite, db
from app.rbac import AccessRole


def _create_admin(app):
    with app.app_context():
        company = Company(name="Empresa Sintética", slug="empresa-camera")
        worksite = Worksite(name="Obra Sintética", company=company)
        admin = User(
            username="admin-camera",
            access_role=AccessRole.ADMIN.value,
            company=company,
            worksite=worksite,
        )
        admin.set_password("secret")
        db.session.add_all([company, worksite, admin])
        db.session.commit()


def _login(client):
    return client.post(
        "/admin/login",
        data={"username": "admin-camera", "password": "secret"},
    )


def test_new_employee_redirects_directly_to_live_biometric_capture(app, client):
    _create_admin(app)
    assert _login(client).status_code == 302

    response = client.post(
        "/admin/users",
        data={
            "username": "operador-camera",
            "password": "secret",
            "name": "Pessoa Sintética",
            "registration": "CAM-001",
            "role": "Operador",
            "access_role": AccessRole.OPERATOR.value,
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Faça a leitura facial para concluir o cadastro".encode("utf-8") in response.data
    assert b'id="camera-preview"' in response.data
    assert b'id="start-enrollment"' in response.data
    assert b'type="file"' not in response.data


def test_biometric_page_offers_only_secure_live_camera(app, client):
    _create_admin(app)
    with app.app_context():
        admin = User.query.filter_by(username="admin-camera").one()
        target = User(
            username="target-camera",
            name="Pessoa Alvo",
            access_role=AccessRole.OPERATOR.value,
            company_id=admin.company_id,
            worksite_id=admin.worksite_id,
        )
        target.set_password("secret")
        db.session.add(target)
        db.session.commit()
        target_id = target.id

    assert _login(client).status_code == 302
    response = client.get(f"/admin/users/{target_id}/biometric")

    assert response.status_code == 200
    assert b'id="start-camera"' in response.data
    assert b'id="camera-preview"' in response.data
    assert b'id="start-enrollment"' in response.data
    assert b"biometric_capture.js" in response.data
    assert b'type="file"' not in response.data
    assert b"Fotos salvas, galeria e arquivos n" in response.data
    assert b"Capturar dados faciais e cadastrar" in response.data
