# reconhecimento_facial/app/routes.py

"""
Este módulo define as rotas de:
 - /form    → exibe o formulário HTML
 - /upload  → recebe e salva arquivo (retorno de texto)
 - /api/face → reconhece rosto e retorna JSON
"""

# Importa o app Flask e a constante UPLOAD_FOLDER (definida em main.py)
from app import app, UPLOAD_FOLDER

# Importa funções para lidar com requisições e respostas
from flask import request, jsonify, render_template

# Importa módulos do sistema de arquivos e localização de pacotes
import os
import site
from pathlib import Path

# Biblioteca de reconhecimento facial
import face_recognition


# ---------------------------------------
# Rota GET /form
# ---------------------------------------
@app.route('/form')
def form():
    """
    Exibe a página 'form.html' com o botão de upload.
    """
    return render_template('form.html')


# ---------------------------------------
# Rota POST /upload
# ---------------------------------------
@app.route('/upload', methods=['POST'])
def upload():
    """
    Recebe um arquivo via multipart/form-data e salva em disco:
    1. Valida existência do campo 'file'
    2. Garante nome de arquivo não vazio
    3. Salva em UPLOAD_FOLDER
    4. Retorna mensagem simples de texto
    """
    # 1️⃣ Validação: existe o campo?
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']

    # 2️⃣ O nome do arquivo não pode estar vazio
    if file.filename == '':
        return 'No selected file', 400

    # 3️⃣ Define o caminho e salva o arquivo
    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)

    # 4️⃣ Retorna confirmação
    return 'File uploaded successfully', 200


# ---------------------------------------
# Rota POST /api/face
# ---------------------------------------
@app.route('/api/face', methods=['POST'])
def api_face():
    """
    API REST para reconhecimento facial:
    1. Validação básica do arquivo
    2. Salvamento no disco
    3. Configuração do modelo do face_recognition
    4. Carregamento da imagem e extração de encodings
    5. Retorno JSON com sucesso/falha
    """
    # 1️⃣ Checa se veio 'file'
    if 'file' not in request.files:
        return jsonify(success=False, message="Arquivo não enviado."), 400

    file = request.files['file']
    # 2️⃣ Checa nome não vazio
    if file.filename == '':
        return jsonify(success=False, message="Nome do arquivo vazio."), 400

    # 3️⃣ Salva o arquivo no disco
    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)

    try:
        # 4️⃣ Indica onde estão os modelos pré-treinados
        model_path = Path(site.getsitepackages()[0]) / "face_recognition_models"
        os.environ["FACE_RECOGNITION_MODEL_LOCATION"] = str(model_path)

        # 5️⃣ Processa a imagem e extrai encodings
        image = face_recognition.load_image_file(save_path)
        faces = face_recognition.face_encodings(image)

        # 6️⃣ Se encontrou encodings, rosto reconhecido
        if faces:
            return jsonify(success=True, message="Rosto reconhecido com sucesso!")
        else:
            return jsonify(success=False, message="Nenhum rosto detectado.")

    except Exception as e:
        # Em caso de erro, devolve JSON com a mensagem de exceção
        return jsonify(success=False, message=f"Erro interno: {e}"), 500
