# reconhecimento_facial/app/routes.py

from app import app, UPLOAD_FOLDER
from flask import request, jsonify, render_template
import os
import site
from pathlib import Path
import face_recognition

# 📝 rota que serve o formulário HTML (se quiser testar via navegador)
@app.route('/form')
def form():
    return render_template('form.html')

# 📝 rota de upload puro (te devolve só texto)
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)
    return 'File uploaded successfully', 200

# 🚀 API REST de reconhecimento facial
@app.route('/api/face', methods=['POST'])
def api_face():
    # 1️⃣ validação básica
    if 'file' not in request.files:
        return jsonify(success=False, message="Arquivo não enviado."), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify(success=False, message="Nome do arquivo vazio."), 400

    # 2️⃣ salva no disco
    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)

    try:
        # 3️⃣ aponta o model do face_recognition
        model_path = Path(site.getsitepackages()[0]) / "face_recognition_models"
        os.environ["FACE_RECOGNITION_MODEL_LOCATION"] = str(model_path)

        # 4️⃣ carrega a imagem e extrai encodings
        image = face_recognition.load_image_file(save_path)
        faces = face_recognition.face_encodings(image)

        if faces:
            return jsonify(success=True, message="Rosto reconhecido com sucesso!")
        else:
            return jsonify(success=False, message="Nenhum rosto detectado.")
    except Exception as e:
        return jsonify(success=False, message=f"Erro interno: {e}"), 500
