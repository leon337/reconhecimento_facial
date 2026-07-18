from datetime import datetime

from flask import current_app, jsonify, render_template, request

from app.models import Ponto, db
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
}


@bp.route("/punch", methods=["GET"])
def punch():
    return render_template("punch.html")


@bp.route("/punch", methods=["POST"])
def punch_submit():
    image = request.files.get("image")
    punch_type = request.form.get("tipo", "").upper()

    if image is None or not image.filename:
        return jsonify(status="error", message="Envie uma imagem da câmera."), 400
    if punch_type not in ALLOWED_TYPES:
        return jsonify(status="error", message="Tipo de ponto inválido."), 400

    result = recognize_registered_user(
        image.stream,
        tolerance=float(current_app.config.get("FACE_MATCH_TOLERANCE", 0.6)),
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
