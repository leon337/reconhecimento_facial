# app/admin/routes.py

import json
import os
import site
from pathlib import Path

import face_recognition
from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

from app.admin import bp
from app.admin.auth import admin_login_required, is_safe_redirect_target
from app.models import User, db

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@bp.route("/login", methods=["GET", "POST"])
def login():
    next_url = request.values.get("next", "")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()

        if user is None or user.role != "admin" or not user.check_password(password):
            flash("Credenciais administrativas inválidas.", "error")
            return render_template("admin/login.html", next_url=next_url), 401

        session.clear()
        session["admin_user_id"] = user.id

        if next_url and is_safe_redirect_target(next_url):
            return redirect(next_url)
        return redirect(url_for("admin.list_users"))

    return render_template("admin/login.html", next_url=next_url)


@bp.route("/logout", methods=["POST"])
@admin_login_required
def logout():
    session.clear()
    flash("Sessão administrativa encerrada.", "success")
    return redirect(url_for("admin.login"))


@bp.route("/users")
@admin_login_required
def list_users():
    users = User.query.all()
    return render_template("admin/users_list.html", users=users)


@bp.route("/users/new", methods=["GET"])
@admin_login_required
def new_user():
    return render_template("admin/users_new.html")


@bp.route("/users", methods=["POST"])
@admin_login_required
def create_user():
    form = request.form
    user = User(
        username=form["username"],
        name=form.get("name"),
        registration=form.get("registration"),
        role=form.get("role"),
        schedule=form.get("schedule"),
        address=form.get("address"),
        pass_type=form.get("pass_type"),
    )
    user.set_password(form["password"])
    db.session.add(user)
    db.session.commit()
    flash("Usuário cadastrado com sucesso.", "success")
    return redirect(url_for("admin.list_users"))


@bp.route("/users/<int:user_id>/biometric", methods=["GET"])
@admin_login_required
def biometric_form(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("admin/users_biometric.html", user=user)


@bp.route("/users/<int:user_id>/biometric", methods=["POST"])
@admin_login_required
def save_biometric(user_id):
    user = User.query.get_or_404(user_id)
    file = request.files.get("file")
    if not file or not allowed_file(file.filename):
        flash("Arquivo inválido.", "error")
        return redirect(url_for("admin.biometric_form", user_id=user_id))

    filename = secure_filename(file.filename)
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    model_path = Path(site.getsitepackages()[0]) / "face_recognition_models"
    os.environ["FACE_RECOGNITION_MODEL_LOCATION"] = str(model_path)

    image = face_recognition.load_image_file(filepath)
    encs = face_recognition.face_encodings(image)
    if not encs:
        flash("Nenhum rosto detectado.", "error")
        return redirect(url_for("admin.biometric_form", user_id=user_id))

    user.face_encoding = json.dumps(encs[0].tolist())
    user.photo_url = url_for("static", filename="uploads/" + filename)
    db.session.commit()

    flash("Biometria cadastrada com sucesso.", "success")
    return redirect(url_for("admin.list_users"))
