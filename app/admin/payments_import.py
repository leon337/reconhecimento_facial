"""Rota de pré-análise de planilhas, sempre sem persistência de dados de células."""
from flask import abort, g, make_response, render_template, request
from app.admin import bp
from app.admin.auth import permission_required
from app.payment_import import MAX_XLSX_BYTES, WorkbookPreviewError, inspect_xlsx
from app.rbac import Permission


@bp.route("/pagamentos/importacoes/analisar", methods=["GET", "POST"])
@permission_required(Permission.PAYMENTS_EDIT)
def payments_import_preview():
    if g.admin_user.company_id is None:
        abort(403, "Vincule a conta a uma empresa.")
    result = None
    if request.method == "POST":
        file = request.files.get("arquivo")
        if file is None or not (file.filename or "").lower().endswith(".xlsx"):
            abort(400, "Selecione um arquivo .xlsx.")
        source = file.stream.read(MAX_XLSX_BYTES + 1)
        if len(source) > MAX_XLSX_BYTES:
            abort(413, "Arquivo acima do limite permitido.")
        try:
            result = inspect_xlsx(source)
        except WorkbookPreviewError as error:
            abort(400, str(error))
        finally:
            del source
    response = make_response(render_template("admin/payments_import.html", preview=result))
    response.headers["Cache-Control"] = "no-store, private"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response
