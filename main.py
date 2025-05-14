# 📦 Importa bibliotecas
import face_recognition
from PIL import Image
from pathlib import Path
from flask import Flask, request, render_template
import site
import os

# 🚀 Inicializa o app Flask
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🌐 Rota do formulário
@app.route("/form")
def form():
    return render_template("form.html")

# 📤 Rota de upload com reconhecimento facial
@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return 'Nenhum arquivo enviado', 400

    file = request.files['file']
    if file.filename == '':
        return 'Arquivo vazio', 400

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    # Define o caminho do modelo de reconhecimento
    model_path = Path(site.getsitepackages()[0]) / "face_recognition_models"
    os.environ["FACE_RECOGNITION_MODEL_LOCATION"] = str(model_path)

    # Carrega imagem e processa
    img = face_recognition.load_image_file(path)
    encodings = face_recognition.face_encodings(img)

    if encodings:
        return '✅ Rosto reconhecido com sucesso!'
    else:
        return '❌ Nenhum rosto detectado.'

# 🔁 Executa o servidor
if __name__ == '__main__':
    app.run(debug=True)
