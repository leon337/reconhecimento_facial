"""Contratos de acesso do Copiloto Potiguar: nenhum comando de escrita de domínio."""
import json
from io import BytesIO
from urllib.error import URLError

import pytest

from app.models import User, db
from app.rbac import AccessRole


def _login(app, client, role):
    with app.app_context():
        user = User(username="copilot-" + role, access_role=role)
        user.set_password("senha-sintetica")
        db.session.add(user)
        db.session.commit()
    response = client.post("/admin/login", data={
        "username": "copilot-" + role,
        "password": "senha-sintetica",
    })
    assert response.status_code == 302


def test_guest_cannot_use_copilot(client):
    assert client.get("/admin/copilot").status_code == 302
    assert client.get("/admin/copilot/meta").status_code == 302
    assert client.post("/admin/copilot/session-token", json={"model": "gemini-3.8-live"}).status_code == 302


def test_operator_without_users_view_is_denied(app, client):
    with app.app_context():
        user = User(username="operator", access_role=AccessRole.OPERATOR.value)
        user.set_password("senha-sintetica")
        db.session.add(user)
        db.session.commit()
    assert client.post("/admin/login", data={"username": "operator", "password": "senha-sintetica"}).status_code == 401
    assert client.get("/admin/copilot").status_code == 302
    assert client.get("/admin/copilot/meta").status_code == 302


def test_workspace_ships_with_feature_disabled(app, client):
    _login(app, client, AccessRole.AUDITOR.value)
    page = client.get("/admin/copilot")
    assert page.status_code == 200
    assert b"potiguar-copilot" in page.data
    assert b"no-store" in page.headers["Cache-Control"].encode()
    assert "wss://generativelanguage.googleapis.com" in page.headers["Content-Security-Policy"]
    info = client.get("/admin/copilot/meta").json
    assert info["enabled"] is False
    assert info["can_create_user"] is False
    assert info["links"]["new_user"] is None
    assert info["mode"] == "guidance_only"


def test_rejects_when_disabled_or_unconfigured(app, client):
    _login(app, client, AccessRole.ADMIN.value)
    with app.app_context():
        app.config["COPILOT_GEMINI_API_KEY"] = "fixture-only"
    assert client.post("/admin/copilot/session-token", json={"model": "gemini-3.8-live"}).status_code == 503
    app.config["COPILOT_ENABLED"] = True
    app.config["COPILOT_GEMINI_API_KEY"] = ""
    # The test must not rely on an external GEMINI_API_KEY environment value.
    from unittest.mock import patch
    with patch("app.copilot.routes.os.environ.get", return_value=None):
        assert client.post("/admin/copilot/session-token", json={"model": "gemini-3.8-live"}).status_code == 503


def test_model_allowlist_and_explicit_short_token(app, client, monkeypatch):
    _login(app, client, AccessRole.ADMIN.value)
    app.config.update(COPILOT_ENABLED=True, COPILOT_GEMINI_API_KEY="fake-provider-key")
    calls = []
    monkeypatch.setattr("app.copilot.routes.provision_live_token", lambda key, model: (
        calls.append((key, model)) or "ephemeral-test-token"
    ))
    assert client.post("/admin/copilot/session-token", json={"model": "fake-model"}).status_code == 400
    response = client.post("/admin/copilot/session-token", data="not-json").status_code
    assert response == 415
    response = client.post("/admin/copilot/session-token", json={"model": "gemini-3.8-live-extended-thinking"})
    assert response.status_code == 200
    assert response.json["token"] == "ephemeral-test-token"
    assert "fake-provider-key" not in response.get_data(as_text=True)
    assert response.headers["Cache-Control"].startswith("no-store")
    assert calls == [("fake-provider-key", "gemini-3.8-live-extended-thinking")]
    assert client.post("/admin/copilot/session-token", json={"model": "gemini-3.8-live"}).status_code == 429


def test_provider_failure_returns_generic_error(app, client, monkeypatch):
    from app.copilot.live import LiveProvisioningError
    _login(app, client, AccessRole.ADMIN.value)
    app.config.update(COPILOT_ENABLED=True, COPILOT_GEMINI_API_KEY="fixture-provider-key")
    def explode(*_):
        raise LiveProvisioningError("provider-sensitive-detail")
    monkeypatch.setattr("app.copilot.routes.provision_live_token", explode)
    res = client.post("/admin/copilot/session-token", json={"model": "gemini-3.8-live"})
    assert res.status_code == 502
    assert "provider-sensitive-detail" not in res.get_data(as_text=True)
    assert "fixture-provider-key" not in res.get_data(as_text=True)


def test_ephemeral_credential_request_is_restricted_and_one_use(monkeypatch):
    from app.copilot import live
    observed = {}
    class FakeResponse:
        def __enter__(self): return BytesIO(b'{"name": "ephemeral-secret"}')
        def __exit__(self, *_): return None
    def fake_open(req, timeout):
        observed["url"] = req.full_url
        observed["headers"] = dict(req.header_items())
        observed["body"] = json.loads(req.data)
        observed["timeout"] = timeout
        return FakeResponse()
    monkeypatch.setattr(live, "urlopen", fake_open)
    assert live.provision_live_token("not-real", "gemini-3.8-live") == "ephemeral-secret"
    assert observed["body"]["uses"] == 1
    assert observed["body"]["liveConnectConstraints"]["model"] == "models/gemini-3.8-live"
    assert observed["url"].startswith("https://")
    assert "not-real" not in observed["url"]
    with pytest.raises(ValueError):
        live.provision_live_token("not-real", "untrusted-model")
