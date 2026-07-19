# app/admin/routes.py

import json
import os
import site
from pathlib import Path
from uuid import uuid4

import face_recognition
from flask import current_app, flash, redirect, render_template, request, session, url_for
from PIL import Image, UnidentifiedImageError

from app.admin import bp
from app.admin.auth import admin_login_required, is_safe_redirect_target, permission_required, sync_admin_scope
from app.biometric_models import BiometricProfile
from app.biometrics import BiometricCryptoError, delete_private_image, encrypt_template, save_private_image
from app.models import Employee, User, db
from app.observability import audit, increment_metric, login_rate_limiter
from app.rbac import AccessRole, Permission

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
ALLOWED_IMAGE_FORMATS = {"JPEG": ".jpg", "PNG": ".png"}


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
    """Compatibilidade: gera nomes não previsíveis sem expor o diretório privado."""
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
    address = request.headers.get("X-Forwarded-For", request.remote_addr) or "unknown"
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
    flash("Colaborador e conta de acesso cadastrados com sucesso.", "success")
    return redirect(url_for("admin.list_users"))


@bp.route("/users/<int:user_id>/biometric", methods=["GET"])
@permission_required(Permission.BIOMETRICS_MANAGE)
def biometric_form(user_id):
    return render_template("admin/users_biometric.html", user=_scoped_user_or_404(user_id))


@bp.route("/users/<int:user_id>/biometric", methods=["POST"])
@permission_required(Permission.BIOMETRICS_MANAGE)
def save_biometric(user_id):
    user = _scoped_user_or_404(user_id)
    file = request.files.get("file")
    if not file or not file.filename or not allowed_file(file.filename):
        flash("Arquivo inválido.", "error")
        return redirect(url_for("admin.biometric_form", user_id=user_id))

    extension = validated_image_extension(file)
    if extension is None:
        flash("O conteúdo enviado não é uma imagem JPEG ou PNG válida.", "error")
        return redirect(url_for("admin.biometric_form", user_id=user_id))

    object_key, filepath = save_private_image(file, extension)
    model_path = Path(site.getsitepackages()[0]) / "face_recognition_models"
    os.environ["FACE_RECOGNITION_MODEL_LOCATION"] = str(model_path)

    try:
        image = face_recognition.load_image_file(filepath)
        encodings = face_recognition.face_encodings(image)
    except (OSError, ValueError):
        delete_private_image(object_key)
        flash("Não foi possível processar a imagem enviada.", "error")
        return redirect(url_for("admin.biometric_form", user_id=user_id))

    if len(encodings) != 1:
        delete_private_image(object_key)
        message = "Nenhum rosto detectado." if not encodings else "Envie uma imagem com apenas um rosto."
        flash(message, "error")
        return redirect(url_for("admin.biometric_form", user_id=user_id))

    try:
        encrypted_template = encrypt_template(json.dumps(encodings[0].tolist()))
    except BiometricCryptoError:
        delete_private_image(object_key)
        current_app.logger.exception("Falha na configuração criptográfica biométrica")
        flash("A biometria não pôde ser protegida. Verifique a configuração segura.", "error")
        return redirect(url_for("admin.biometric_form", user_id=user_id)), 503

    profile = user.biometric_profile or BiometricProfile(user=user)
    previous_object_key = profile.image_object_key
    profile.encrypted_template = encrypted_template
    profile.image_object_key = object_key
    profile.algorithm_version = "face_recognition-1"
    profile.active = True
    db.session.add(profile)
    actor = User.query.get(session.get("admin_user_id"))
    audit("admin.biometric.enroll", "success", actor=actor, target_type="user", target_id=user.id)
    db.session.commit()
    if previous_object_key and previous_object_key != object_key:
        delete_private_image(previous_object_key)

    flash("Biometria protegida e cadastrada com sucesso.", "success")
    return redirect(url_for("admin.list_users"))
