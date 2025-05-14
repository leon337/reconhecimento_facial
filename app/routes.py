from app import app
from flask import request
import os

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)
    return 'File uploaded successfully', 200
