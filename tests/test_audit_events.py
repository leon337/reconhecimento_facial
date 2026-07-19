import pytest

from app.audit_models import AuditEvent
from app.models import User, db


def test_failed_admin_login_creates_audit_event(app, client):
    response = client.post(
        "/admin/login",
        data={"username": "inexistente", "password": "incorreta"},
    )

    assert response.status_code == 401
    with app.app_context():
        event = AuditEvent.query.filter_by(action="admin.login", outcome="failure").one()
        assert event.request_id
        assert "incorreta" not in (event.metadata_json or "")


def test_successful_login_and_logout_are_audited(app, client):
    with app.app_context():
        user = User(username="audit-admin", role="admin")
        user.set_password("senha-segura")
        db.session.add(user)
        db.session.commit()

    login = client.post(
        "/admin/login",
        data={"username": "audit-admin", "password": "senha-segura"},
    )
    logout = client.post("/admin/logout")

    assert login.status_code == 302
    assert logout.status_code == 302
    with app.app_context():
        actions = [event.action for event in AuditEvent.query.order_by(AuditEvent.id).all()]
        assert "admin.login" in actions
        assert "admin.logout" in actions


def test_audit_event_cannot_be_updated_or_deleted(app):
    with app.app_context():
        event = AuditEvent(request_id="req-immutable", action="test", outcome="success")
        db.session.add(event)
        db.session.commit()

        event.outcome = "changed"
        with pytest.raises(ValueError, match="audit_event_is_append_only"):
            db.session.commit()
        db.session.rollback()

        persisted = AuditEvent.query.filter_by(request_id="req-immutable").one()
        db.session.delete(persisted)
        with pytest.raises(ValueError, match="audit_event_is_append_only"):
            db.session.commit()
        db.session.rollback()
