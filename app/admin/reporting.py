"""Relatório de conferência e exportação somente leitura, RBAC por empresa/obra."""
import csv
import io
from datetime import date, datetime, timedelta, time, timezone
from zoneinfo import ZoneInfo

from flask import abort, Response, render_template, request, session
from sqlalchemy.orm import joinedload

from app.admin import bp
from app.admin.auth import permission_required
from app.attendance_reporting import summarize_punches
from app.models import Ponto, User
from app.rbac import Permission

RECIFE = ZoneInfo("America/Recife")
MAX_DAYS = 31
MAX_RECORDS = 10000


def _interval():
    today = datetime.now(RECIFE).date()
    end_text = request.args.get("fim") or today.isoformat()
    start_text = request.args.get("inicio") or (today - timedelta(days=6)).isoformat()
    try:
        start = date.fromisoformat(start_text)
        end = date.fromisoformat(end_text)
    except (TypeError, ValueError):
        abort(400, "Datas inválidas")
    if start > end or (end - start).days >= MAX_DAYS:
        abort(400, "Intervalo máximo de 31 dias")
    return start, end


def _utc_midnight(day):
    return datetime.combine(day, time.min, tzinfo=RECIFE).astimezone(timezone.utc).replace(tzinfo=None)


def _scoped_users():
    query = User.query.filter(User.employee_id.isnot(None))
    company = session.get("admin_company_id")
    worksite = session.get("admin_worksite_id")
    if company is None:
        query = query.filter(User.company_id.is_(None))
    else:
        query = query.filter(User.company_id == company)
        if worksite is not None:
            query = query.filter(User.worksite_id == worksite)
    return query


def _records():
    start, end = _interval()
    requested_id = request.args.get("funcionario", "").strip()
    if requested_id and (not requested_id.isdigit() or int(requested_id) < 1):
        abort(400, "Funcionário inválido")
    users = _scoped_users().order_by(User.name, User.id).all()
    allowed = {u.id for u in users}
    employee_id = int(requested_id) if requested_id else None
    if employee_id is not None and employee_id not in allowed:
        abort(404)
    query = Ponto.query.options(joinedload(Ponto.user)).filter(
        Ponto.user_id.in_(allowed),
        Ponto.timestamp >= _utc_midnight(start) - timedelta(days=1),
        Ponto.timestamp < _utc_midnight(end + timedelta(days=1)) + timedelta(days=1),
    )
    if employee_id is not None:
        query = query.filter(Ponto.user_id == employee_id)
    # Limite explícito evita exportação parcial apresentada como completa.
    points = query.order_by(Ponto.timestamp.asc(), Ponto.id.asc()).limit(MAX_RECORDS + 1).all()
    if len(points) > MAX_RECORDS:
        abort(413, "Muitos registros; reduza o período ou selecione um funcionário")
    return start, end, users, employee_id, points


def _filtered_points(points, start, end):
    for point in points:
        day = point.timestamp.replace(tzinfo=timezone.utc).astimezone(RECIFE).date()
        if start <= day <= end:
            yield point


def _safe_csv_cell(value):
    text = str(value or "")
    # Neutraliza fórmula em planilhas sem suprimir o valor original.
    if text.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


@bp.get("/relatorios")
@permission_required(Permission.PUNCH_VIEW)
def reports():
    start, end, users, employee_id, points = _records()
    daily = summarize_punches(points, start, end)
    total_seconds = sum(r["seconds"] for r in daily)
    return render_template(
        "admin/relatorios.html", start=start.isoformat(), end=end.isoformat(),
        users=users, employee_id=employee_id, daily=daily,
        flagged=sum(bool(r["issues"]) for r in daily),
        calculated=f'{int(total_seconds // 3600):02d}:{int(total_seconds % 3600 // 60):02d}',
    )


@bp.get("/relatorios/exportar.csv")
@permission_required(Permission.PUNCH_VIEW)
def export_punches():
    start, end, _, _, points = _records()
    output = io.StringIO(newline="")
    writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["ID", "Funcionário", "Usuário", "Tipo", "Data e hora (Recife)", "Fuso horário"])
    for point in _filtered_points(points, start, end):
        when = point.timestamp.replace(tzinfo=timezone.utc).astimezone(RECIFE)
        writer.writerow([
            point.id,
            _safe_csv_cell(point.user.name or point.user.username),
            _safe_csv_cell(point.user.username),
            point.tipo,
            when.strftime("%d/%m/%Y %H:%M:%S"),
            "America/Recife",
        ])
    csv_bytes = ("\ufeff" + output.getvalue()).encode("utf-8")
    response = Response(csv_bytes, mimetype="text/csv; charset=utf-8")
    response.headers["Content-Disposition"] = f'attachment; filename="potiguar-pontos-{start}-{end}.csv"'
    response.headers["Cache-Control"] = "no-store, private"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response
