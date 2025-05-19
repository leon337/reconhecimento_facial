#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import site
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.models import db               # importa a instância db

def create_app():
    # 1) Inicializa o Flask e configura pasta de uploads dentro de static/
    app = Flask(__name__, static_folder='static')
        # depois de criar app...
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ponto.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # cria as tabelas no banco se ainda não existirem
    with app.app_context():
        db.create_all()
        
    upload_folder = os.path.join(app.static_folder, 'uploads')
    app.config['UPLOAD_FOLDER'] = upload_folder
    os.makedirs(upload_folder, exist_ok=True)

    # 2) Registra as rotas definidas em app/routes.py
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    # Debug ligado para facilitar desenvolvimento; em produção, use um WSGI real
    app.run(debug=True, host='0.0.0.0', port=5000)
