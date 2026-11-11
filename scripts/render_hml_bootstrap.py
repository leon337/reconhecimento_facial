"""Inicializa APENAS uma homologação efêmera com credenciais sintéticas.

Nunca ativar em produção. Não recebe nem armazena a chave Gemini.
"""
from __future__ import annotations

import os

from app.models import User, db
from app.rbac import AccessRole
from main import app


def bootstrap() -> None:
    if os.environ.get("POTIGUAR_HML_DEMO") != "1":
        raise RuntimeError("Homologação não autorizada neste ambiente")
    if os.environ.get("APP_ENV") != "development":
        raise RuntimeError("A demonstração não pode usar modo de produção")
    if os.environ.get("POTIGUAR_COPILOT_ENABLED", "0") != "0":
        raise RuntimeError("IA externa deve permanecer desabilitada no Render")
    username = os.environ.get("POTIGUAR_DEMO_USERNAME", "")
    password = os.environ.get("POTIGUAR_DEMO_PASSWORD", "")
    if not 5 <= len(username) <= 60 or not 20 <= len(password) <= 180:
        raise RuntimeError("Credenciais sintéticas precisam estar configuradas")
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("POTIGUAR_COPILOT_VAULT_DIR"):
        raise RuntimeError("Nunca disponibilizar a chave Gemini na demonstração pública")

    with app.app_context():
        user = User.query.filter_by(username=username).one_or_none()
        if user is None:
            user = User(username=username, access_role=AccessRole.SUPER_ADMIN.value)
            db.session.add(user)
        # Reinicializar senha ao reiniciar a instância pública, sem logá-la.
        user.set_password(password)
        db.session.commit()
    print("Potiguar: homologação sintética inicializada (sem dados reais).", flush=True)


if __name__ == "__main__":
    bootstrap()
