# app/admin/__init__.py

from flask import Blueprint

bp = Blueprint("admin", __name__, url_prefix="/admin")

from app.admin import routes  # noqa: E402,F401
from app.admin import biometric_cleanup  # noqa: E402,F401
