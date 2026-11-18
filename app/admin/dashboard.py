"""Painel e histórico de pontos: consultas administrativas somente leitura."""
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from flask import abort, render_template, request, session
from sqlalchemy.orm import joinedload

from app.admin import bp
from app.admin.simulation import simulated_ids
from app.attendance_reporting import summarize_punches
from app.admin.auth import permission_required
from app.biometric_models import BiometricProfile
from app.models import Employee, Ponto, User
from app.rbac import Permission

RECIFE = ZoneInfo("America/Recife")
PAGE_SIZE = 50


def _scoped(query, model):
    """Um administrador sem empresa vê apenas cadastros sem empresa (homologação)."""
    company_id = session.get("admin_company_id")
    worksite_id = session.get("admin_worksite_id")
    if company_id is None:
        return query.filter(model.company_id.is_(None))
    query = query.filter(model.company_id == company_id)
    if worksite_id is not None:
        query = query.filter(model.worksite_id == worksite_id)
    return query


def _local_time(timestamp):
    if timestamp is None:
        return "—"
    return timestamp.replace(tzinfo=timezone.utc).astimezone(RECIFE).strftime("%d/%m/%Y %H:%M:%S")


def _utc_interval(day):
    start_local = datetime.combine(day, time.min, tzinfo=RECIFE)
    end_local = start_local + timedelta(days=1)
    return (
        start_local.astimezone(timezone.utc).replace(tzinfo=None),
        end_local.astimezone(timezone.utc).replace(tzinfo=None),
    )


def _punches():
    return _scoped(Ponto.query.options(joinedload(Ponto.user)), Ponto)


@bp.get("/dashboard")
@permission_required(Permission.USERS_VIEW)
def dashboard():
    today = datetime.now(RECIFE).date()
    start, end = _utc_interval(today)
    punches = _punches()
    employee_users = _scoped(
        User.query.filter(User.employee_id.isnot(None)), User
    )
    profiles = (
        BiometricProfile.query.join(User, BiometricProfile.user_id == User.id)
        .filter(BiometricProfile.active.is_(True), User.employee_id.isnot(None))
    )
    company_id = session.get("admin_company_id")
    worksite_id = session.get("admin_worksite_id")
    if company_id is None:
        profiles = profiles.filter(User.company_id.is_(None))
    else:
        profiles = profiles.filter(User.company_id == company_id)
        if worksite_id is not None:
            profiles = profiles.filter(User.worksite_id == worksite_id)
    latest = punches.order_by(Ponto.timestamp.desc(), Ponto.id.desc()).limit(8).all()
    period_start = datetime.now(RECIFE).date() - timedelta(days=6)
    begin, _ = _utc_interval(period_start)
    _, end = _utc_interval(datetime.now(RECIFE).date())
    recent = punches.filter(Ponto.timestamp >= begin, Ponto.timestamp < end).order_by(Ponto.timestamp).limit(10001).all()
    truncated = len(recent) > 10000
    daily = [] if truncated else summarize_punches(recent, period_start, datetime.now(RECIFE).date())
    return render_template(
        "admin/dashboard.html",
        employees=employee_users.count(),
        biometrics=profiles.count(),
        punches_today=punches.filter(Ponto.timestamp >= start, Ponto.timestamp < end).count(),
        punches_total=punches.count(),
        latest=latest,
        synthetic=simulated_ids(latest),
        recent_simulated=bool(simulated_ids(recent)),
        daily=daily,
        summary_truncated=truncated,
        today=today.strftime("%d/%m/%Y"),
        local_time=_local_time,
    )


@bp.get("/pontos")
@permission_required(Permission.USERS_VIEW)
def history():
    day_text = request.args.get("data", "").strip()
    punch_type = request.args.get("tipo", "").strip().upper()
    page_text = request.args.get("pagina", "1").strip()
    if punch_type not in ("", "ENTRADA", "SAIDA") or not page_text.isdigit():
        abort(400)
    page = int(page_text)
    if not 1 <= page <= 10000:
        abort(400)
    query = _punches()
    if day_text:
        try:
            day = date.fromisoformat(day_text)
        except ValueError:
            abort(400)
        start, end = _utc_interval(day)
        query = query.filter(Ponto.timestamp >= start, Ponto.timestamp < end)
    if punch_type:
        query = query.filter(Ponto.tipo == punch_type)
    total = query.count()
    points = query.order_by(Ponto.timestamp.desc(), Ponto.id.desc()).limit(PAGE_SIZE).offset((page - 1) * PAGE_SIZE).all()
    return render_template(
        "admin/pontos.html",
        points=points, total=total, page=page,
        has_next=page * PAGE_SIZE < total,
        day_text=day_text, punch_type=punch_type, local_time=_local_time, synthetic=simulated_ids(points),
    )
