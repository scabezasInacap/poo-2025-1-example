# app.py

from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db, User # Importa db y User de models.py
from controllers import main_bp, auth_bp # Importa los Blueprints

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar Flask-SQLAlchemy
    db.init_app(app)

    # Inicializar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' # Ruta a la que se redirige si no está logeado
    login_manager.login_message = "Por favor, inicia sesión para acceder a esta página."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        """Callback requerido por Flask-Login para cargar un usuario."""
        return User.query.get(int(user_id))

    # Registrar los Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app

if __name__ == '__main__':
    app = create_app()

    # Creación de tablas de la base de datos (solo una vez)
    # Se recomienda ejecutar esto en un shell de Python o en un script de migración
    with app.app_context():
        db.create_all()
        print("Tablas de la base de datos creadas (si no existían).")

    app.run(debug=True) # debug=True para desarrollo, cambiar a False en producción