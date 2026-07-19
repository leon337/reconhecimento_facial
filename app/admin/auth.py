from functools import wraps
from urllib.parse import urljoin, urlparse

from flask import abort, flash, g, redirect, request, session, url_for

from app.models import User
from app.rbac import Permission


def is_safe_redirect_target(target: str) -> bool:
    """Aceita apenas redirecionamentos internos da própria aplicação."""
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in {"http", "https"} and host_url.netloc == redirect_url.netloc


def sync_admin_scope(user: User) -> None:
    """Mantém o escopo organizacional da sessão alinhado ao usuário autenticado."""
    session["admin_company_id"] = user.company_id
    session["admin_worksite_id"] = user.worksite_id


def current_admin_user() -> User | None:
    user_id = session.get("admin_user_id")
    return User.query.get(user_id) if user_id is not None else None


def admin_login_required(view):
    """Exige uma conta válida com ao menos uma permissão administrativa."""

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        user = current_admin_user()

        if user is None or not user.can(Permission.USERS_VIEW):
            session.clear()
            flash("Faça login com uma conta autorizada para continuar.", "warning")
            return redirect(url_for("admin.login", next=request.full_path.rstrip("?")))

        g.admin_user = user
        sync_admin_scope(user)
        return view(*args, **kwargs)

    return wrapped_view


def permission_required(permission: Permission):
    """Bloqueia a operação quando o papel não possui a permissão exigida."""

    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            user = current_admin_user()
            if user is None:
                session.clear()
                return redirect(url_for("admin.login", next=request.full_path.rstrip("?")))
            if not user.can(permission):
                abort(403)

            g.admin_user = user
            sync_admin_scope(user)
            return view(*args, **kwargs)

        return wrapped_view

    return decorator
