"""Emissão de token efêmero de acesso ao Gemini Live API.

A chave permanente permanece no servidor. O token é de uso único, com
janela curta para iniciar sessão. Nenhum evento de ponto é acessado.
"""

import json
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen

ALLOWED_MODELS = frozenset({
    "gemini-3.8-live",
    "gemini-3.8-live-extended-thinking",
})
TOKEN_URL = "https://generativelanguage.googleapis.com/v1beta/auth_tokens"


class LiveProvisioningError(RuntimeError):
    """Falha de provisionamento sem detalhes sensíveis do fornecedor."""


def provision_live_token(api_key: str, model: str) -> str:
    """Emite token efêmero de uso único, sem registrar a chave permanente.

    O catálogo permite modelos 3.8 Live, mas a implementação v1beta do
    auth_tokens do projeto rejeitou liveConnectConstraints (HTTP 400,
    campo desconhecido) em 2026-11-11. Restringimos o modelo no servidor,
    com token de uma única sessão, início em 60 s e validade máxima de
    15 min; o provedor NÃO restringe o modelo neste contrato.
    """
    if model not in ALLOWED_MODELS:
        raise ValueError("modelo não autorizado")
    if not api_key:
        raise LiveProvisioningError("chave do provedor não configurada")

    now = datetime.now(timezone.utc)
    payload = {
        "uses": 1,
        "newSessionExpireTime": (now + timedelta(seconds=60)).isoformat().replace("+00:00", "Z"),
        "expireTime": (now + timedelta(minutes=15)).isoformat().replace("+00:00", "Z"),
    }
    req = Request(
        TOKEN_URL,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
    )
    try:
        with urlopen(req, timeout=12) as response:
            data = json.load(response)
    except (OSError, ValueError) as exc:
        raise LiveProvisioningError("não foi possível iniciar a sessão Live") from exc
    token = data.get("name") if isinstance(data, dict) else None
    if not isinstance(token, str) or not token:
        raise LiveProvisioningError("resposta inválida do serviço Live")
    return token
