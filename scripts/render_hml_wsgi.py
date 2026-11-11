"""Gateway HTTP Basic autenticado para homologação isolada no Render.

Demonstração do fluxo Flask. Nunca usar como autenticação de produção.
Sem credencial Gemini, sem dados trabalhistas ou biometria reais.
"""
from __future__ import annotations

import base64
import hmac
import os

from werkzeug.wrappers import Response
from main import app as flask_app

if os.environ.get("POTIGUAR_HML_DEMO") != "1":
    raise RuntimeError("Gateway restrito à homologação")
if os.environ.get("APP_ENV") != "development":
    raise RuntimeError("Gateway de demonstração não opera em produção")

username = os.environ.get("POTIGUAR_DEMO_USERNAME", "")
password = os.environ.get("POTIGUAR_DEMO_PASSWORD", "")
if not username or len(password) < 20:
    raise RuntimeError("Configure credenciais antes de publicar")

flask_app.config.update(
    SESSION_COOKIE_SECURE=True,
    PREFERRED_URL_SCHEME="https",
    COPILOT_ENABLED=False,
)


class DemoGateway:
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        # O health check é público somente para permitir monitoramento da
        # plataforma Render; não retorna detalhes de credenciais.
        if environ.get("PATH_INFO") == "/health":
            return self.application(environ, start_response)

        header = environ.get("HTTP_AUTHORIZATION", "")
        allowed = False
        if header.startswith("Basic ") and len(header) <= 512:
            try:
                decoded = base64.b64decode(header[6:], validate=True).decode("utf-8")
                user, supplied = decoded.split(":", 1)
                allowed = (
                    hmac.compare_digest(user, username)
                    and hmac.compare_digest(supplied, password)
                )
            except (ValueError, UnicodeError):
                allowed = False

        if not allowed:
            response = Response(
                "Acesso restrito à homologação Potiguar.",
                status=401,
                headers={
                    "WWW-Authenticate": 'Basic realm="Potiguar Homologacao", charset="UTF-8"',
                    "Cache-Control": "no-store",
                    "X-Robots-Tag": "noindex, nofollow, noarchive",
                },
            )
            return response(environ, start_response)

        # O login da aplicação Flask continua independente desta barreira.
        return self.application(environ, start_response)


app = DemoGateway(flask_app)
