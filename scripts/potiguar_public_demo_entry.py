"""Entrypoint exclusivo da instância pública sintética e descartável.

Não altera main:app, a homologação protegida nem produção.
"""
from main import app
from app.public_demo import install_public_demo

install_public_demo(app)
