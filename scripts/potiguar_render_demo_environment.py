"""Fail-closed environment guard for the isolated, synthetic Render demo.

No access to real databases, administrative accounts, biometrics or Gemini keys.
This module prepares environment BEFORE importing the regular Flask application.
"""
import base64
import hashlib
import hmac
import os


REQUIRED = {
    "POTIGUAR_RENDER_SYNTHETIC_ONLY": "1",
    "POTIGUAR_PUBLIC_DEMO": "1",
    "APP_ENV": "development",
    "POTIGUAR_DEPLOYMENT_ROLE": "development",
    "POTIGUAR_HML_PUBLIC_HTTPS": "1",
    "POTIGUAR_COPILOT_ENABLED": "1",
    "POTIGUAR_COPILOT_ACTIONS_ENABLED": "1",
    "DATABASE_URL": "sqlite:////app/instance/ponto.db",
    "WEB_CONCURRENCY": "1",
}


def prepare_render_demo_environment(environ=None):
    """Fail before Flask import unless every synthetic isolation condition holds."""
    env = os.environ if environ is None else environ
    for name, expected in REQUIRED.items():
        if env.get(name) != expected:
            raise RuntimeError("Synthetic Render demo preflight failed: " + name)
    if env.get("GEMINI_API_KEY") or env.get("POTIGUAR_COPILOT_VAULT_DIR"):
        raise RuntimeError("Permanent Gemini credentials require a separate storage/quota gate")
    if env.get("BIOMETRIC_ENCRYPTION_KEY"):
        raise RuntimeError("Biometric keys are forbidden in the synthetic demo")
    secret = env.get("SECRET_KEY", "")
    if len(secret) < 32 or secret == "development-only-change-me":
        raise RuntimeError("A persistent, randomly generated SECRET_KEY is required")
    # Stable across reboots when Render's SECRET_KEY remains unchanged.
    # No second secret is stored in Git or managed separately.
    seed = hmac.new(
        secret.encode("utf-8"),
        b"potiguar-render-synthetic-onboarding-fernet-v1",
        hashlib.sha256,
    ).digest()
    fernet_key = base64.urlsafe_b64encode(seed).decode("ascii")
    prior = env.get("POTIGUAR_ONBOARDING_FERNET_KEY", "")
    if prior and prior != fernet_key:
        raise RuntimeError("Conflicting synthetic onboarding encryption key")
    env["POTIGUAR_ONBOARDING_FERNET_KEY"] = fernet_key
