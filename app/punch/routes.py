import time
from datetime import datetime

from flask import current_app, jsonify, render_template, request

from app.liveness import analyze_blink_liveness, consume_challenge, issue_challenge
from app.models import Ponto, db
from app.observability import increment_metric
from app.punch import bp
from app.punch.rules import check_duplicate_punch
from app.punch.service import recognize_encoding

ALLOWED_TYPES = {"ENTRADA", "SAIDA"}
ERROR_MESSAGES = {
    "invalid_frame": "Quadro inválido ou não processável.",
    "invalid_frame_count": "A sequência da câmera está incompleta. Tente novamente.",
    "no_face": "Nenhum rosto foi detectado.",
    "multiple_faces": "Mantenha apenas uma pessoa diante da câmera.",
    "landmarks_unavailable": "Não foi possível validar os movimentos do rosto.",
    "liveness_failed": "Prova de vida não confirmada. Olhe para a câmera e pisque uma vez.",
    "poor_lighting": "Iluminação inadequada. Posicione-se em um local mais claro.",
    "blurry_frame": "Imagem desfocada. Mantenha o rosto parado e tente novamente.",
    "face_too_small": "Aproxime o rosto da câmera.",
    "encoding_failed": "Não foi possível gerar a leitura biométrica.",
    "invalid_encoding": "Leitura biométrica inválida.",
    "no_registered_faces": "Nenhuma biometria está cadastrada.",
    "unknown_face": "Rosto não reconhecido.",
    "company_scope_required": "Informe a empresa antes de selecionar uma obra.",
    "challenge_invalid": "Desafio inválido. Reinicie a verificação.",
    "challenge_expired": "O desafio expirou. Reinicie a verificação.",
    "challenge_purpose_mismatch": "Desafio incompatível com esta operação.",
    "challenge_subject_mismatch": "Desafio incompatível com este usuário.",
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


@bp.route("/punch", methods=["GET"])
def punch():
    return render_template("punch.html")


@bp.route("/punch/challenge", methods=["GET"])
def punch_challenge():
    return jsonify(issue_challenge("punch"))


@bp.route("/punch", methods=["POST"])
def punch_submit():
    started = time.monotonic()
    frames = request.files.getlist("frames")
    punch_type = request.form.get("tipo", "").upper()
    challenge_id = request.form.get("challenge_id", "")
    company_id = _optional_positive_int("company_id")
    worksite_id = _optional_positive_int("worksite_id")

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
    if not challenge_id:
        return jsonify(status="error", code="challenge_invalid", message=ERROR_MESSAGES["challenge_invalid"]), 400

    challenge_ok, challenge_reason = consume_challenge(challenge_id, "punch")
    if not challenge_ok:
        return jsonify(
            status="error",
            code=challenge_reason,
            message=ERROR_MESSAGES[challenge_reason],
        ), 400

    liveness = analyze_blink_liveness(frames)
    if not liveness.passed:
        increment_metric("punch_liveness_failure_total")
        return jsonify(
            status="error",
            code=liveness.reason,
            message=ERROR_MESSAGES.get(liveness.reason, "Prova de vida não confirmada."),
            processing_ms=int((time.monotonic() - started) * 1000),
        ), 422

    result = recognize_encoding(
        liveness.encoding,
        tolerance=float(current_app.config.get("FACE_MATCH_TOLERANCE", 0.6)),
        company_id=company_id,
        worksite_id=worksite_id,
    )
    if result.user is None:
        increment_metric("punch_recognition_failure_total")
        return jsonify(
            status="error",
            code=result.reason,
            message=ERROR_MESSAGES.get(result.reason, "Rosto não reconhecido."),
            processing_ms=int((time.monotonic() - started) * 1000),
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
            processing_ms=int((time.monotonic() - started) * 1000),
        ), 409

    record = Ponto.from_user(result.user, tipo=punch_type, timestamp=now)
    db.session.add(record)
    db.session.commit()

    processing_ms = int((time.monotonic() - started) * 1000)
    increment_metric("punch_liveness_success_total")
    if processing_ms <= int(current_app.config.get("PUNCH_TARGET_MILLISECONDS", 8000)):
        increment_metric("punch_target_met_total")
    else:
        increment_metric("punch_target_missed_total")

    return jsonify(
        status="ok",
        message=f"{punch_type.title()} registrada com sucesso para {result.user.name or result.user.username}.",
        user={"id": result.user.id, "name": result.user.name or result.user.username},
        punch={"id": record.id, "tipo": record.tipo, "timestamp": record.timestamp.isoformat()},
        liveness={
            "passed": True,
            "blink_count": liveness.blink_count,
            "quality_score": liveness.quality_score,
        },
        match_distance=result.distance,
        processing_ms=processing_ms,
        target_met=processing_ms <= int(current_app.config.get("PUNCH_TARGET_MILLISECONDS", 8000)),
    ), 201
