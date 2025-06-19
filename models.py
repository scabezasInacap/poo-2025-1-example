# models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users' # Nombre de la tabla en la base de datos
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.Text)

    def set_password(self, password):
        """Genera un hash de la contraseña para almacenarla de forma segura."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica una contraseña dada contra el hash almacenado."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """Representación legible del objeto User."""
        return f'<User {self.username}>'