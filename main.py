import os
import site
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.models import db
from app.admin.routes import bp as admin_bp

def create_app():
    # 1) Cria a app e configura pastas de static e templates
    app = Flask(
        __name__,
        static_folder='static',
        template_folder='templates'
    )

    # 2) Chave secreta usada para sessões, cookies assinados e proteção CSRF
    # Em produção: export SECRET_KEY no seu .env ou no ambiente de hosting
    app.config['SECRET_KEY'] = os.environ.get(
        'SECRET_KEY',
        'rtI7sWd8gNFY63K9bW9AAZaeHmZa5oacyGQ7LNTTUPI'  # substitua por uma string aleatória forte
    )

    # 3) Configuração do banco de dados SQLite (em instance/ponto.db)
    basedir = Path(__file__).resolve().parent
    instance_dir = basedir / 'instance'
    instance_dir.mkdir(exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{instance_dir / 'ponto.db'}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 4) Pasta onde os uploads (imagens) serão salvos
    upload_folder = basedir / 'static' / 'uploads'
    upload_folder.mkdir(parents=True, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = str(upload_folder)

    # 5) Configura onde o face_recognition vai buscar os modelos
    model_path = Path(site.getsitepackages()[0]) / 'face_recognition_models'
    os.environ['FACE_RECOGNITION_MODEL_LOCATION'] = str(model_path)

    # 6) Inicializa o SQLAlchemy
    db.init_app(app)

    # 7) Registra o blueprint do admin em /admin
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    from app.punch import bp as punch_bp
    app.register_blueprint(punch_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    # Garante que as tabelas existam
    with app.app_context():
        db.create_all()
    # Executa em debug para desenvolvimento
    app.run(host='0.0.0.0', port=5000, debug=True)
