"""Render-only WSGI entrypoint for the disposable Potiguar synthetic demo.

Never use main:app as the service entrypoint. All isolation checks happen
before Flask/database/routes initialize.
"""
from scripts.potiguar_render_demo_environment import prepare_render_demo_environment

prepare_render_demo_environment()

from scripts.potiguar_public_demo_entry import app  # noqa: E402,F401
