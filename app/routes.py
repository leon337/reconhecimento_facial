# app/routes.py

import os
import site
from pathlib import Path
from flask import Blueprint, current_app, request, render_template, jsonify, url_for
from werkzeug.utils import secure_filename
import face_recognition

bp = Blueprint('routes', __name__)

# Extensões permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """Retorna True se a extensão do arquivo for permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/form', methods=['GET'])
def form():
    """Exibe o formulário de upload."""
    return render_template('form.html')

@bp.route('/upload', methods=['POST'])
def upload():
    """
    Recebe o arquivo, executa reconhecimento facial
    e renderiza o template `result.html` com feedback visual.
    """
    file = request.files.get('file')
    # Validação básica
    if not file or file.filename == '' or not allowed_file(file.filename):
        return render_template('result.html',
                               filename=None,
                               success=False,
                               message="Arquivo inválido ou não enviado.")

    # Salva em static/uploads
    filename = secure_filename(file.filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    # Configura o modelo pré-treinado
    model_path = Path(site.getsitepackages()[0]) / 'face_recognition_models'
    os.environ['FACE_RECOGNITION_MODEL_LOCATION'] = str(model_path)

    # Carrega a imagem e detecta rostos
    image = face_recognition.load_image_file(filepath)
    faces = face_recognition.face_locations(image)
    success = len(faces) > 0
    message = "Rosto reconhecido com sucesso!" if success else "Nenhum rosto detectado."

    return render_template('result.html',
                           filename=filename,
                           success=success,
                           message=message)

@bp.route('/api/face', methods=['POST'])
def api_face():
    """
    Endpoint JSON puro para reconhecimento:
    retorna { success: bool, message: str }.
    """
    file = request.files.get('file')
    if not file or file.filename == '' or not allowed_file(file.filename):
        return jsonify(success=False, message="Arquivo inválido ou não enviado."), 400

    filename = secure_filename(file.filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    model_path = Path(site.getsitepackages()[0]) / 'face_recognition_models'
    os.environ['FACE_RECOGNITION_MODEL_LOCATION'] = str(model_path)

    image = face_recognition.load_image_file(filepath)
    encodings = face_recognition.face_encodings(image)

    if encodings:
        return jsonify(success=True, message="Rosto reconhecido com sucesso!")
    else:
        return jsonify(success=False, message="Nenhum rosto detectado.")
