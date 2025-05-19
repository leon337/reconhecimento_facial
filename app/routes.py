# reconhecimento_facial/app/routes.py

"""
Define as três principais rotas:
1. GET  /form      → exibe o formulário de upload
2. POST /upload    → recebe o arquivo, salva em disco e renderiza feedback visual
3. POST /api/face  → recebe o arquivo, faz reconhecimento e retorna JSON
"""

from flask import current_app, request, render_template, jsonify
from werkzeug.utils import secure_filename
import os
import site
from pathlib import Path
import face_recognition

# A pasta onde os uploads serão salvos
UPLOAD_FOLDER = current_app.config.get('UPLOAD_FOLDER', 'uploads')
# Extensões de imagem permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    """Retorna True se o arquivo tiver extensão permitida."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/form', methods=['GET'])
def form():
    """
    Exibe o form para enviar imagem.
    Apenas renderiza o template `form.html`.
    """
    return render_template('form.html')


@app.route('/upload', methods=['POST'])
def upload():
    """
    Recebe o arquivo via POST multipart/form-data:
    1. Valida se veio arquivo e se a extensão é permitida.
    2. Gera nome seguro e salva em UPLOAD_FOLDER.
    3. Usa face_recognition para detectar rostos.
    4. Retorna renderização do template `result.html`,
       passando `filename`, `success` e `message`.
    """
    file = request.files.get('file')
    # 1️⃣ Validação básica
    if not file or file.filename == '' or not allowed_file(file.filename):
        return render_template('result.html',
                               filename=None,
                               success=False,
                               message="Arquivo inválido ou não enviado.")
    # 2️⃣ Salva o upload
    filename = secure_filename(file.filename)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # 3️⃣ Prepara o modelo do face_recognition
    model_path = Path(site.getsitepackages()[0]) / "face_recognition_models"
    os.environ["FACE_RECOGNITION_MODEL_LOCATION"] = str(model_path)

    # 4️⃣ Carrega a imagem e faz a detecção
    image = face_recognition.load_image_file(filepath)
    faces = face_recognition.face_locations(image)

    success = len(faces) > 0
    message = "Rosto reconhecido com sucesso!" if success else "Nenhum rosto detectado."

    # 5️⃣ Renderiza feedback visual
    return render_template('result.html',
                           filename=filename,
                           success=success,
                           message=message)


@app.route('/api/face', methods=['POST'])
def api_face():
    """
    Expondo um endpoint JSON puro para reconhecimento:
    - Mesmas validações de arquivo.
    - Salva o arquivo igual ao upload.
    - Retorna JSON { success: bool, message: str }.
    """
    file = request.files.get('file')
    if not file or file.filename == '' or not allowed_file(file.filename):
        return jsonify(success=False, message="Arquivo inválido ou não enviado."), 400

    filename = secure_filename(file.filename)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        model_path = Path(site.getsitepackages()[0]) / "face_recognition_models"
        os.environ["FACE_RECOGNITION_MODEL_LOCATION"] = str(model_path)

        image = face_recognition.load_image_file(filepath)
        encodings = face_recognition.face_encodings(image)

        if encodings:
            return jsonify(success=True, message="Rosto reconhecido com sucesso!")
        else:
            return jsonify(success=False, message="Nenhum rosto detectado.")
    except Exception as e:
        return jsonify(success=False, message=f"Erro interno: {e}"), 500
