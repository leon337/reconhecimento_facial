# app/admin/routes.py

import json
from uuid import uuid4

from flask import current_app, flash, jsonify, redirect, render_template, request, session, url_for
from PIL import Image, UnidentifiedImageError

from app.admin import bp
from app.admin.auth import admin_login_required, is_safe_redirect_target, permission_required, sync_admin_scope
from app.biometric_models import BiometricProfile
from app.biometrics import BiometricCryptoError, delete_private_image, encrypt_template, save_private_image_bytes
from app.face_enrollment import analyze_face_enrollment
from app.liveness import consume_challenge, issue_challenge
from app.models import Employee, User, db
from app.observability import audit, increment_metric, login_rate_limiter
from app.punch.service import find_duplicate_biometric
from app.rbac import AccessRole, Permission

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
ALLOWED_IMAGE_FORMATS = {"JPEG": ".jpg", "PNG": ".png"}


# Mantidos para compatibilidade de integrações administrativas antigas. O fluxo
# operacional da FASE 10.1 não expõe seleção de arquivos ao usuário.
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validated_image_extension(file_storage):
    try:
        image = Image.open(file_storage.stream)
        image.verify()
        extension = ALLOWED_IMAGE_FORMATS.get(image.format)
    except (UnidentifiedImageError, OSError, ValueError):
        extension = None
    finally:
        file_storage.stream.seek(0)
    return extension


def unique_upload_name(extension):
    return f"{uuid4().hex}{extension}"


def _scoped_user_query():
    query = User.query
    company_id = session.get("admin_company_id")
    worksite_id = session.get("admin_worksite_id")
    if company_id is not None:
        query = query.filter_by(company_id=company_id)
        if worksite_id is not None:
            query = query.filter_by(worksite_id=worksite_id)
    return query


def _scoped_user_or_404(user_id):
    return _scoped_user_query().filter_by(id=user_id).first_or_404()


def _login_key(username: str) -> str:
    address = request.remote_addr or "unknown"
    return f"{address}:{username.lower()}"


@bp.route("/login", methods=["GET", "POST"])
def login():
    next_url = request.values.get("next", "")
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        key = _login_key(username)
        limit = current_app.config["LOGIN_RATE_LIMIT_ATTEMPTS"]
        window = current_app.config["LOGIN_RATE_LIMIT_WINDOW_SECONDS"]

        if login_rate_limiter.blocked(key, limit=limit, window_seconds=window):
            increment_metric("admin_login_rate_limited_total")
            audit("admin.login", "blocked", metadata={"username": username[:80]})
            db.session.commit()
            flash("Muitas tentativas. Aguarde antes de tentar novamente.", "error")
            return render_template("admin/login.html", next_url=next_url), 429

        user = User.query.filter_by(username=username).first()
        if user is None or not user.can(Permission.USERS_VIEW) or not user.check_password(password):
            login_rate_limiter.register_failure(key)
            increment_metric("admin_login_failure_total")
            audit("admin.login", "failure", actor=user, metadata={"username": username[:80]})
            db.session.commit()
            flash("Credenciais administrativas inválidas.", "error")
            return render_template("admin/login.html", next_url=next_url), 401

        login_rate_limiter.clear(key)
        session.clear()
        session.permanent = True
        session["admin_user_id"] = user.id
        sync_admin_scope(user)
        increment_metric("admin_login_success_total")
        audit("admin.login", "success", actor=user)
        db.session.commit()
        if next_url and is_safe_redirect_target(next_url):
            return redirect(next_url)
        return redirect(url_for("admin.list_users"))
    return render_template("admin/login.html", next_url=next_url)


@bp.route("/logout", methods=["POST"])
@admin_login_required
def logout():
    user = User.query.get(session.get("admin_user_id"))
    audit("admin.logout", "success", actor=user)
    db.session.commit()
    session.clear()
    flash("Sessão administrativa encerrada.", "success")
    return redirect(url_for("admin.login"))


@bp.route("/users")
@permission_required(Permission.USERS_VIEW)
def list_users():
    return render_template("admin/users_list.html", users=_scoped_user_query().all())


@bp.route("/users/new", methods=["GET"])
@permission_required(Permission.USERS_CREATE)
def new_user():
    return render_template("admin/users_new.html")


@bp.route("/users", methods=["POST"])
@permission_required(Permission.USERS_CREATE)
def create_user():
    form = request.form
    company_id = session.get("admin_company_id")
    worksite_id = session.get("admin_worksite_id")
    job_title = form.get("role")
    employee = Employee(
        name=form.get("name") or form["username"],
        registration=form.get("registration") or None,
        job_title=job_title,
        schedule=form.get("schedule"),
        address=form.get("address"),
        pass_type=form.get("pass_type"),
        company_id=company_id,
        worksite_id=worksite_id,
    )
    user = User(
        username=form["username"],
        access_role=form.get("access_role") or AccessRole.OPERATOR.value,
        employee=employee,
        name=employee.name,
        registration=employee.registration,
        role=job_title,
        schedule=employee.schedule,
        address=employee.address,
        pass_type=employee.pass_type,
        company_id=company_id,
        worksite_id=worksite_id,
    )
    user.set_password(form["password"])
    db.session.add_all([employee, user])
    db.session.flush()
    actor = User.query.get(session.get("admin_user_id"))
    audit("admin.user.create", "success", actor=actor, target_type="user", target_id=user.id)
    db.session.commit()
    flash("Funcionário salvo. Faça a leitura facial para concluir o cadastro.", "success")
    return redirect(url_for("admin.biometric_form", user_id=user.id))


@bp.route("/users/<int:user_id>/biometric", methods=["GET"])
@permission_required(Permission.BIOMETRICS_MANAGE)
def biometric_form(user_id):
    return render_template("admin/users_biometric.html", user=_scoped_user_or_404(user_id))


@bp.route("/users/<int:user_id>/biometric/challenge", methods=["GET"])
@permission_required(Permission.BIOMETRICS_MANAGE)
def biometric_challenge(user_id):
    user = _scoped_user_or_404(user_id)
    challenge = issue_challenge("enrollment", subject_id=user.id)
    challenge.update(
        {
            "action": "FACE_SCAN",
            "prompt": "Olhe para a câmera e mantenha o rosto firme por alguns segundos.",
            "frame_count": int(current_app.config.get("ENROLLMENT_FRAME_COUNT", 8)),
            "capture_interval_ms": int(current_app.config.get("ENROLLMENT_CAPTURE_INTERVAL_MS", 160)),
        }
    )
    return jsonify(challenge)


@bp.route("/users/<int:user_id>/biometric", methods=["POST"])
@permission_required(Permission.BIOMETRICS_MANAGE)
def save_biometric(user_id):
    user = _scoped_user_or_404(user_id)
    challenge_id = request.form.get("challenge_id", "")
    challenge_ok, _challenge_reason = consume_challenge(
        challenge_id,
        "enrollment",
        subject_id=user.id,
    )
    if not challenge_ok:
        flash("Captura inválida ou expirada. Reinicie a leitura facial.", "error")
        return redirect(url_for("admin.biometric_form", user_id=user_id))

    enrollment = analyze_face_enrollment(request.files.getlist("frames"))
    if not enrollment.passed:
        increment_metric("biometric_enrollment_face_failure_total")
        messages = {
            "no_face": "Nenhum rosto detectado.",
            "multiple_faces": "Mantenha apenas uma pessoa diante da câmera.",
            "insufficient_quality_frames": "Não houve leituras faciais nítidas suficientes. Melhore a iluminação e mantenha o rosto parado.",
            "inconsistent_face": "As leituras não representam um único rosto consistente. Reinicie o cadastro.",
            "invalid_frame_count": "A sequência da câmera ficou incompleta. Reinicie o cadastro.",
        }
        flash(messages.get(enrollment.reason, "Não foi possível gerar o perfil biométrico facial."), "error")
        return redirect(url_for("admin.biometric_form", user_id=user_id))

    duplicate = find_duplicate_biometric(
        enrollment.encoding,
        company_id=user.company_id,
        exclude_user_id=user.id,
        tolerance=float(current_app.config.get("FACE_DUPLICATE_TOLERANCE", 0.45)),
    )
    if duplicate.user is not None:
        actor = User.query.get(session.get("admin_user_id"))
        audit(
            "admin.biometric.enroll",
            "duplicate_rejected",
            actor=actor,
            target_type="user",
            target_id=user.id,
            metadata={"duplicate_user_id": duplicate.user.id, "distance": duplicate.distance},
        )
        db.session.commit()
        flash("Este rosto já está associado a outro funcionário.", "error")
        return redirect(url_for("admin.biometric_form", user_id=user_id))

    object_key, _ = save_private_image_bytes(enrollment.best_frame_jpeg, ".jpg")
    try:
        encrypted_template = encrypt_template(json.dumps(enrollment.encoding.tolist()))
    except BiometricCryptoError:
        delete_private_image(object_key)
        current_app.logger.exception("Falha na configuração criptográfica biométrica")
        flash("A biometria não pôde ser protegida. Verifique a configuração segura.", "error")
        return redirect(url_for("admin.biometric_form", user_id=user_id)), 503

    profile = user.biometric_profile or BiometricProfile(user=user)
    previous_object_key = profile.image_object_key
    profile.encrypted_template = encrypted_template
    profile.image_object_key = object_key
    profile.algorithm_version = "face_recognition-multiframe-3"
    profile.active = True
    db.session.add(profile)
    actor = User.query.get(session.get("admin_user_id"))
    audit(
        "admin.biometric.enroll",
        "success",
        actor=actor,
        target_type="user",
        target_id=user.id,
        metadata={
            "capture_method": "live_multiframe",
            "valid_frames": enrollment.valid_frames,
            "quality_score": enrollment.quality_score,
            "max_intra_distance": enrollment.max_intra_distance,
            "processing_ms": enrollment.duration_ms,
        },
    )
    db.session.commit()
    if previous_object_key and previous_object_key != object_key:
        delete_private_image(previous_object_key)

    increment_metric("biometric_enrollment_face_success_total")
    flash("Perfil biométrico facial protegido e cadastrado com sucesso.", "success")
    return redirect(url_for("admin.list_users"))
