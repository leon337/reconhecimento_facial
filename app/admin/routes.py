# app/admin/routes.py

import os, json, site
from pathlib import Path
from flask import (
    render_template, request, redirect,
    url_for, flash, current_app
)
from werkzeug.utils import secure_filename
import face_recognition

from app.admin import bp
from app.models import db, User

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )

@bp.route('/users')
def list_users():
    users = User.query.all()
    return render_template('admin/users_list.html', users=users)

@bp.route('/users/new', methods=['GET'])
def new_user():
    return render_template('admin/users_new.html')

@bp.route('/users', methods=['POST'])
def create_user():
    form = request.form
    user = User(
        username=form['username'],
        name=form.get('name'),
        registration=form.get('registration'),
        role=form.get('role'),
        schedule=form.get('schedule'),
        address=form.get('address'),
        pass_type=form.get('pass_type')
    )
    user.set_password(form['password'])
    db.session.add(user)
    db.session.commit()
    flash('Usuário cadastrado com sucesso.', 'success')
    return redirect(url_for('admin.list_users'))

@bp.route('/users/<int:user_id>/biometric', methods=['GET'])
def biometric_form(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('admin/users_biometric.html', user=user)

@bp.route('/users/<int:user_id>/biometric', methods=['POST'])
def save_biometric(user_id):
    user = User.query.get_or_404(user_id)
    file = request.files.get('file')
    if not file or not allowed_file(file.filename):
        flash('Arquivo inválido.', 'error')
        return redirect(url_for('admin.biometric_form', user_id=user_id))

    filename = secure_filename(file.filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    # Configura modelo para face_recognition
    model_path = Path(site.getsitepackages()[0]) / 'face_recognition_models'
    os.environ['FACE_RECOGNITION_MODEL_LOCATION'] = str(model_path)

    image = face_recognition.load_image_file(filepath)
    encs = face_recognition.face_encodings(image)
    if not encs:
        flash('Nenhum rosto detectado.', 'error')
        return redirect(url_for('admin.biometric_form', user_id=user_id))

    # Salva encoding e URL da foto
    user.face_encoding = json.dumps(encs[0].tolist())
    user.photo_url = url_for('static', filename='uploads/' + filename)
    db.session.commit()

    flash('Biometria cadastrada com sucesso.', 'success')
    return redirect(url_for('admin.list_users'))
