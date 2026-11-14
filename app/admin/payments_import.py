"""Rota de pré-análise de planilhas, sempre sem persistência de dados de células."""
from flask import abort, g, make_response, render_template, request
from app.admin import bp
from app.admin.auth import permission_required
from app.payment_import import MAX_XLSX_BYTES, WorkbookPreviewError, inspect_xlsx
from app.payment_mapping import inspect_payment_mapping
from app.payment_v2_link import V2EmployeeRef, simulate_v2_link, MAX_EMPLOYEES_IN_SCOPE, STATUS_DESCRIPTIONS
from app.models import Employee, Worksite, db
from app.onboarding_models import EmployeeOnboarding
from sqlalchemy import and_
from app.rbac import Permission


def _scope_worksites():
    user = g.admin_user
    worksites = Worksite.query.filter_by(company_id=user.company_id, active=True)
    if user.worksite_id is not None:
        worksites = worksites.filter_by(id=user.worksite_id)
    return worksites.order_by(Worksite.name, Worksite.id).all()


def _requested_worksite():
    """Escopo da V2: jamais aceitar seleção de outra empresa/obra."""
    raw = request.form.get("obra", "").strip()
    if raw and (not raw.isdecimal() or int(raw) <= 0):
        abort(400, "Obra inválida.")
    selected = int(raw) if raw else g.admin_user.worksite_id
    if g.admin_user.worksite_id is not None and selected != g.admin_user.worksite_id:
        abort(403)
    if selected is not None and Worksite.query.filter_by(
        id=selected, company_id=g.admin_user.company_id, active=True
    ).first() is None:
        abort(404)
    return selected


def _v2_registry(worksite_id):
    """Somente Employee e existência da ficha V2; nunca descriptografa payload."""
    query = db.session.query(
        Employee.id, Employee.name, Employee.active, EmployeeOnboarding.employee_id,
    ).outerjoin(
        EmployeeOnboarding,
        and_(EmployeeOnboarding.employee_id == Employee.id,
             EmployeeOnboarding.company_id == Employee.company_id),
    ).filter(Employee.company_id == g.admin_user.company_id)
    if worksite_id is not None:
        query = query.filter(Employee.worksite_id == worksite_id)
    rows = query.limit(MAX_EMPLOYEES_IN_SCOPE + 1).all()
    if len(rows) > MAX_EMPLOYEES_IN_SCOPE:
        abort(413, "O cadastro V2 excede o limite de prévia.")
    return [
        V2EmployeeRef(employee_id=employee_id, full_name=name,
                      active=active, has_v2_record=v2_id is not None)
        for employee_id, name, active, v2_id in rows
    ]


@bp.route("/pagamentos/importacoes/analisar", methods=["GET", "POST"])
@permission_required(Permission.PAYMENTS_EDIT)
def payments_import_preview():
    if g.admin_user.company_id is None:
        abort(403, "Vincule a conta a uma empresa.")
    result = None
    mapping = None
    v2_link = None
    selected_worksite = g.admin_user.worksite_id
    if request.method == "POST":
        file = request.files.get("arquivo")
        if file is None or not (file.filename or "").lower().endswith(".xlsx"):
            abort(400, "Selecione um arquivo .xlsx.")
        source = file.stream.read(MAX_XLSX_BYTES + 1)
        if len(source) > MAX_XLSX_BYTES:
            abort(413, "Arquivo acima do limite permitido.")
        try:
            result = inspect_xlsx(source)
            mode = request.form.get("mapear", "0")
            if mode in ("1", "2"):
                mapping = inspect_payment_mapping(source, preflight=result)
            if mode == "2":
                selected_worksite = _requested_worksite()
                v2_link = simulate_v2_link(
                    source, mapping, _v2_registry(selected_worksite)
                )
        except WorkbookPreviewError as error:
            abort(400, str(error))
        finally:
            del source
    response = make_response(render_template(
        "admin/payments_import.html", preview=result, mapping=mapping,
        v2_link=v2_link, v2_status_labels=STATUS_DESCRIPTIONS,
        selected_worksite=selected_worksite, worksites=_scope_worksites(),
        restricted_to_worksite=g.admin_user.worksite_id is not None,
    ))
    response.headers["Cache-Control"] = "no-store, private"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response
