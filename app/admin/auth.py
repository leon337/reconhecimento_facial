from functools import wraps
from urllib.parse import urljoin, urlparse

from flask import flash, redirect, request, session, url_for

from app.models import User


def is_safe_redirect_target(target: str) -> bool:
    """Aceita apenas redirecionamentos internos da própria aplicação."""
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in {"http", "https"} and host_url.netloc == redirect_url.netloc


def admin_login_required(view):
    """Exige uma sessão válida vinculada a um usuário com papel de administrador."""

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        user_id = session.get("admin_user_id")
        user = User.query.get(user_id) if user_id is not None else None

        if user is None or user.role != "admin":
            session.pop("admin_user_id", None)
            flash("Faça login como administrador para continuar.", "warning")
            return redirect(url_for("admin.login", next=request.full_path.rstrip("?")))

        return view(*args, **kwargs)

    return wrapped_view
