"""Conferência semanal de jornada (fase 01) — sem cálculo ou execução financeira."""
from datetime import date, time

from flask import abort, g, redirect, render_template, request, url_for
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.admin import bp
from app.admin.auth import permission_required
from app.models import Employee, Worksite, db
from app.observability import audit
from app.payment_models import PaymentPeriod, PaymentWorkEntry
from app.payment_time import calculate_worked_minutes, duration_label
from app.rbac import Permission


def _company_id() -> int:
    """Contas sem empresa (legado/homologação) não podem operar folha."""
    company = g.admin_user.company_id
    if company is None:
        abort(403, "Vincule a conta administrativa a uma empresa.")
    return company


def _periods_query():
    query = PaymentPeriod.query.filter_by(company_id=_company_id())
    worksite = g.admin_user.worksite_id
    if worksite is not None:
        query = query.filter_by(worksite_id=worksite)
    return query


def _get_period(period_id: int) -> PaymentPeriod:
    period = _periods_query().filter_by(id=period_id).first()
    if period is None:
        abort(404)
    return period


def _worksites():
    query = Worksite.query.filter_by(company_id=_company_id(), active=True)
    if g.admin_user.worksite_id is not None:
        query = query.filter_by(id=g.admin_user.worksite_id)
    return query.order_by(Worksite.name).all()


def _employee_query(period: PaymentPeriod):
    query = Employee.query.filter_by(company_id=period.company_id, active=True)
    if period.worksite_id is not None:
        query = query.filter_by(worksite_id=period.worksite_id)
    if g.admin_user.worksite_id is not None:
        query = query.filter_by(worksite_id=g.admin_user.worksite_id)
    return query


def _private(response):
    response.headers["Cache-Control"] = "no-store, private"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@bp.get("/pagamentos")
@permission_required(Permission.PAYMENTS_VIEW)
def payments_home():
    periods = _periods_query().order_by(
        PaymentPeriod.start_date.desc(), PaymentPeriod.id.desc()
    ).limit(100).all()
    return _private(render_template_response(
        "admin/payments.html", periods=periods, worksites=_worksites(),
        can_edit=g.admin_user.can(Permission.PAYMENTS_EDIT),
        restricted_to_worksite=g.admin_user.worksite_id is not None
    ))


@bp.post("/pagamentos/periodos")
@permission_required(Permission.PAYMENTS_EDIT)
def payments_create_period():
    company_id = _company_id()
    try:
        start_date = date.fromisoformat(request.form["inicio"])
        end_date = date.fromisoformat(request.form["fim"])
        if (end_date - start_date).days != 6:
            raise ValueError("O período deve abranger exatamente sete dias.")
        raw_worksite = request.form.get("obra", "").strip()
        worksite_id = int(raw_worksite) if raw_worksite else None
        if worksite_id is not None and worksite_id <= 0:
            raise ValueError("Obra inválida.")
    except (KeyError, TypeError, ValueError):
        abort(400, "Informe duas datas válidas e sete dias consecutivos.")

    if g.admin_user.worksite_id is not None and worksite_id != g.admin_user.worksite_id:
        abort(403, "Conta limitada a outra obra.")
    if worksite_id is not None and not Worksite.query.filter_by(
        id=worksite_id, company_id=company_id, active=True
    ).first():
        abort(404)

    key = PaymentPeriod.key(company_id, worksite_id, start_date, end_date)
    if PaymentPeriod.query.filter_by(scope_key=key).first():
        abort(409, "Já existe um período para este intervalo e escopo.")

    period = PaymentPeriod(
        company_id=company_id, worksite_id=worksite_id, scope_key=key,
        start_date=start_date, end_date=end_date, status="draft",
        created_by=g.admin_user.id,
    )
    db.session.add(period)
    try:
        db.session.flush()
        audit(
            "payments.period.created", "success", actor=g.admin_user,
            target_type="payment_period", target_id=period.id,
            metadata={"start": start_date.isoformat(), "end": end_date.isoformat()},
        )
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(409, "Período duplicado.")
    return redirect(url_for("admin.payments_period", period_id=period.id), code=303)


@bp.get("/pagamentos/periodos/<int:period_id>")
@permission_required(Permission.PAYMENTS_VIEW)
def payments_period(period_id):
    period = _get_period(period_id)
    entries_query = PaymentWorkEntry.query.filter_by(period_id=period.id)
    count = entries_query.count()
    minutes = db.session.query(func.sum(PaymentWorkEntry.worked_minutes)).filter(
        PaymentWorkEntry.period_id == period.id
    ).scalar() or 0
    entries = entries_query.order_by(
        PaymentWorkEntry.work_date.desc(), PaymentWorkEntry.id.desc()
    ).limit(500).all()
    return _private(render_template_response(
        "admin/payments_period.html",
        period=period, entries=entries, total_count=count,
        is_truncated=count > 500, worked=duration_label(minutes),
        employees=_employee_query(period).order_by(Employee.name, Employee.id).all(),
        can_edit=g.admin_user.can(Permission.PAYMENTS_EDIT),
        duration_label=duration_label,
    ))


@bp.post("/pagamentos/periodos/<int:period_id>/jornadas")
@permission_required(Permission.PAYMENTS_EDIT)
def payments_add_entry(period_id):
    period = _get_period(period_id)
    if period.status != "draft":
        abort(409, "Somente períodos em rascunho aceitam lançamentos.")
    try:
        raw_employee = request.form["funcionario"].strip()
        if not raw_employee.isdigit() or int(raw_employee) < 1:
            raise ValueError("Funcionário inválido.")
        employee_id = int(raw_employee)
        work_date = date.fromisoformat(request.form["data"])
        times = [
            time.fromisoformat(request.form[field])
            for field in ("entrada", "intervalo_inicio", "intervalo_fim", "saida")
        ]
        minutes = calculate_worked_minutes(*times)
    except (KeyError, TypeError, ValueError):
        abort(400, "Data ou horários inválidos. Confira entrada, intervalo e saída.")

    if not period.start_date <= work_date <= period.end_date:
        abort(400, "Data fora do período semanal.")
    employee = _employee_query(period).filter_by(id=employee_id).first()
    if employee is None:
        abort(404)
    if PaymentWorkEntry.query.filter_by(
        period_id=period.id, employee_id=employee.id, work_date=work_date
    ).first():
        abort(409, "Já existe lançamento desse funcionário nesta data.")

    entry = PaymentWorkEntry(
        period_id=period.id, company_id=period.company_id,
        worksite_id=employee.worksite_id, employee_id=employee.id,
        work_date=work_date,
        entry_time=times[0], break_start=times[1], break_end=times[2],
        exit_time=times[3], worked_minutes=minutes,
        created_by=g.admin_user.id,
    )
    db.session.add(entry)
    try:
        db.session.flush()
        audit(
            "payments.entry.created", "success", actor=g.admin_user,
            target_type="payment_work_entry", target_id=entry.id,
            metadata={"work_date": work_date.isoformat(), "worked_minutes": minutes},
        )
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(409, "Lançamento duplicado.")
    return redirect(url_for("admin.payments_period", period_id=period.id), code=303)


def render_template_response(template, **context):
    """Adiciona cabeçalhos para impedir cache de dados trabalhistas."""
    from flask import make_response
    return make_response(render_template(template, **context))
