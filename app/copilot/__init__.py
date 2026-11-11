"""Copiloto Potiguar — integração isolada, sem comandos de escrita no domínio."""

from flask import Blueprint

bp = Blueprint("copilot", __name__)

from app.copilot import routes  # noqa: E402,F401
