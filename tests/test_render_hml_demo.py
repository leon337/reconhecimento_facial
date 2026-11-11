"""Testa isolamento da homologação e negação do acesso anônimo."""
import base64
import os
import subprocess
import sys

from werkzeug.test import Client
from werkzeug.wrappers import Response


def test_demo_bootstrap_refuses_without_flag():
    env = os.environ.copy()
    env.pop("POTIGUAR_HML_DEMO", None)
    env["APP_ENV"] = "development"
    script = "from scripts.render_hml_bootstrap import bootstrap; bootstrap()"
    result = subprocess.run(
        [sys.executable, "-c", script],
        env=env, capture_output=True, text=True, timeout=12,
    )
    assert result.returncode != 0


def test_demo_gateway_blocks_without_credentials(monkeypatch):
    monkeypatch.setenv("POTIGUAR_HML_DEMO", "1")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("POTIGUAR_DEMO_USERNAME", "potiguar-demo")
    monkeypatch.setenv("POTIGUAR_DEMO_PASSWORD", "demo-pass-" + "x" * 35)
    from scripts.render_hml_wsgi import DemoGateway

    def application(environ, start_response):
        return Response("demo-ok", status=200)(environ, start_response)

    client = Client(DemoGateway(application), Response)
    assert client.get("/admin/copilot").status_code == 401
    assert client.get("/health").status_code == 200
    assert client.get(
        "/admin/copilot", headers={"Authorization": "Basic inválido"}
    ).status_code == 401
    correct = base64.b64encode(("potiguar-demo:" + "demo-pass-" + "x" * 35).encode()).decode()
    assert client.get(
        "/admin/copilot", headers={"Authorization": "Basic " + correct}
    ).status_code == 200
