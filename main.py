# 📚 Importa bibliotecas necessárias
import face_recognition
from PIL import Image
from pathlib import Path
from flask import Flask, request, render_template, jsonify
import os
import site

# 🚀 Inicializa o app Flask
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 📄 Rota do formulário
@app.route('/form')
def form():
    return render_template("form.html")

# 🧠 Rota de upload com reconhecimento facial
@app.route('/upload', methods=["POST"])
def upload():
    if 'file' not in request.files:
        return 'Nenhum arquivo enviado', 400

    file = request.files['file']
    if file.filename == '':
        return 'Nenhum arquivo selecionado', 400
# ─────────── ROTA REST DE RECONHECIMENTO FACIAL (JSON) ───────────
@app.route('/api/face', methods=['POST'])
def api_face():
    # 1) Validar se veio arquivo
    if 'file' not in request.files:
        return jsonify(success=False, message="Arquivo não enviado."), 400

    file = request.files['file']
    # 2) Validar nome
    if file.filename == '':
        return jsonify(success=False, message="Nome do arquivo vazio."), 400

    # 3) Salvar imagem no disco
    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)

    try:
        # 4) Ajustar onde o face_recognition encontra seus modelos
        model_path = Path(site.getsitepackages()[0]) / "face_recognition_models"
        os.environ["FACE_RECOGNITION_MODEL_LOCATION"] = str(model_path)

        # 5) Carregar e extrair encodings
        image = face_recognition.load_image_file(save_path)
        faces = face_recognition.face_encodings(image)

        # 6) Se achou algum encoding, sucesso; se não, "nenhum rosto"
        if faces:
            return jsonify(success=True, message="Rosto reconhecido com sucesso!"), 200
        else:
            return jsonify(success=False, message="Nenhum rosto detectado."), 200

    except Exception as e:
        # 7) Erro genérico
        return jsonify(success=False, message=f"Erro interno: {e}"), 500
# ────────────────────────────────────────────────────────────────────

# ▶️ Executa o app
if __name__ == '__main__':
    app.run(debug=True)
