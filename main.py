# 📚 Importa bibliotecas necessárias
import face_recognition
from PIL import Image
from pathlib import Path
from flask import Flask, request, render_template
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

    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)

    # 📌 Alteração da Fase A3 começa aqui:
    model_path = Path(site.getsitepackages()[0]) / "face_recognition_models"
    os.environ["FACE_RECOGNITION_MODEL_LOCATION"] = str(model_path)
    img = face_recognition.load_image_file(save_path)
    encodings = face_recognition.face_encodings(img)

    if encodings:
        return "<h2 style='color:green;'>✅ Rosto reconhecido com sucesso!</h2>"
    else:
        return "<h2 style='color:red;'>❌ Nenhum rosto detectado.</h2>"
    # 📌 Alteração da Fase A3 termina aqui

# ▶️ Executa o app
if __name__ == '__main__':
    app.run(debug=True)
