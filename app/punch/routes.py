from datetime import datetime

from flask import current_app, jsonify, render_template, request

from app.models import Company, Ponto, Worksite, db
from app.punch import bp
from app.punch.rules import check_duplicate_punch
from app.punch.service import recognize_registered_user

ALLOWED_TYPES = {"ENTRADA", "SAIDA"}
ERROR_MESSAGES = {
    "invalid_image": "Imagem inválida ou não processável.",
    "no_face": "Nenhum rosto foi detectado.",
    "multiple_faces": "Mantenha apenas uma pessoa diante da câmera.",
    "no_registered_faces": "Nenhuma biometria está cadastrada.",
    "unknown_face": "Rosto não reconhecido.",
    "company_scope_required": "Informe a empresa antes de selecionar uma obra.",
    "company_not_found": "Empresa não encontrada.",
    "worksite_not_found": "Obra não encontrada.",
    "worksite_company_mismatch": "A obra não pertence à empresa informada.",
}


def _optional_positive_int(field_name):
    raw_value = request.form.get(field_name)
    if raw_value in (None, ""):
        return None

    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return None

    return value if value > 0 else None


def _validate_organizational_scope(company_id, worksite_id):
    """Valida IDs organizacionais informados sem afetar chamadas legadas sem escopo."""
    if company_id is None:
        return None

    company = db.session.get(Company, company_id)
    if company is None:
        return "company_not_found"

    if worksite_id is None:
        return None

    worksite = db.session.get(Worksite, worksite_id)
    if worksite is None:
        return "worksite_not_found"
    if worksite.company_id != company_id:
        return "worksite_company_mismatch"

    return None


@bp.route("/punch", methods=["GET"])
def punch():
    return render_template("punch.html")


@bp.route("/punch", methods=["POST"])
def punch_submit():
    image = request.files.get("image")
    punch_type = request.form.get("tipo", "").upper()
    company_id = _optional_positive_int("company_id")
    worksite_id = _optional_positive_int("worksite_id")

    if image is None or not image.filename:
        return jsonify(status="error", message="Envie uma imagem da câmera."), 400
    if punch_type not in ALLOWED_TYPES:
        return jsonify(status="error", message="Tipo de ponto inválido."), 400
    if request.form.get("worksite_id") not in (None, "") and worksite_id is None:
        return jsonify(status="error", message="Obra inválida."), 400
    if request.form.get("company_id") not in (None, "") and company_id is None:
        return jsonify(status="error", message="Empresa inválida."), 400
    if worksite_id is not None and company_id is None:
        return jsonify(
            status="error",
            code="company_scope_required",
            message=ERROR_MESSAGES["company_scope_required"],
        ), 400

    scope_error = _validate_organizational_scope(company_id, worksite_id)
    if scope_error is not None:
        return jsonify(
            status="error",
            code=scope_error,
            message=ERROR_MESSAGES[scope_error],
        ), 400

    result = recognize_registered_user(
        image.stream,
        tolerance=float(current_app.config.get("FACE_MATCH_TOLERANCE", 0.6)),
        company_id=company_id,
        worksite_id=worksite_id,
    )
    if result.user is None:
        return jsonify(
            status="error",
            code=result.reason,
            message=ERROR_MESSAGES[result.reason],
        ), 422

    now = datetime.utcnow()
    duplicate = check_duplicate_punch(
        user_id=result.user.id,
        now=now,
        window_seconds=int(
            current_app.config.get("PUNCH_DUPLICATE_WINDOW_SECONDS", 60)
        ),
    )
    if duplicate.blocked:
        return jsonify(
            status="error",
            code="duplicate_punch",
            message="Aguarde antes de registrar um novo ponto.",
            retry_after_seconds=duplicate.retry_after_seconds,
        ), 409

    record = Ponto.from_user(result.user, tipo=punch_type, timestamp=now)
    db.session.add(record)
    db.session.commit()

    return jsonify(
        status="ok",
        message=f"{punch_type.title()} registrada com sucesso.",
        user={"id": result.user.id, "name": result.user.name or result.user.username},
        punch={"id": record.id, "tipo": record.tipo, "timestamp": record.timestamp.isoformat()},
    ), 201
