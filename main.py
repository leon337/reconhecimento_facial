# Importa bibliotecas necessárias
import face_recognition
from PIL import Image
from pathlib import Path
import site
import os

# Define o caminho do modelo de reconhecimento
model_path = Path(site.getsitepackages()[0]) / "face_recognition_models"
os.environ["FACE_RECOGNITION_MODEL_LOCATION"] = str(model_path)

# Caminho da imagem (precisa estar na mesma pasta do script)
img_path = "face.jpg"

# Carrega a imagem e gera os encodings faciais
img = face_recognition.load_image_file(img_path)
encodings = face_recognition.face_encodings(img)

# Verifica se encontrou um rosto
if encodings:
    print("✅ Rosto processado com sucesso.")
else:
    print("❌ Nenhum rosto detectado.")
