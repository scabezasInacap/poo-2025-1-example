# config.py

import os

class Config:
    # Clave secreta para la seguridad de las sesiones de Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una_clave_secreta_muy_dificil_de_adivinar'

    # Configuración de la base de datos MySQL
    # Formato: mysql+pymysql://usuario:contraseña@host/nombre_db
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:admin@localhost/mi_app_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Desactiva el seguimiento de modificaciones de objetos