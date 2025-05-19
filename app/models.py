# app/models.py

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name          = db.Column(db.String(120), nullable=True)
    registration  = db.Column(db.String(50), nullable=True)    # matrícula
    role          = db.Column(db.String(80), nullable=True)    # função
    schedule      = db.Column(db.String(120), nullable=True)   # horário
    address       = db.Column(db.String(200), nullable=True)   # residência
    pass_type     = db.Column(db.String(50),  nullable=True)   # tipo de passagem
    face_encoding = db.Column(db.Text,    nullable=True)       # JSON com encoding
    photo_url     = db.Column(db.String(200), nullable=True)    # URL da foto de referência

    pontos = db.relationship('Ponto', backref='user', lazy=True)

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)

class Ponto(db.Model):
    __tablename__ = 'pontos'
    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    tipo      = db.Column(db.String(10), nullable=False)  # 'ENTRADA' ou 'SAÍDA'
