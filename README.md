# PYTHON CON FLASK EN POO

Herramientas

* [Visual Studio Code](https://code.visualstudio.com/download)

* [MySQL Workbench](https://dev.mysql.com/downloads/workbench/)

* [Video completo de la implementación del código en INACAP](https://inacapmailcl-my.sharepoint.com/:f:/g/personal/sebastian_cabezas07_inacapmail_cl/Eg-Ov-A-tbxHma-1AKweOfYBDD4tVdA41Dxnqv5IXC1tuA?e=PPcYvp)

## 0. Credenciales MySQL en INACAP

1. Ejecute XAMPP y haga click en start en mysql.
2. Cree una nueva conexión en MySQL Workbench e Ingrese las siguientes credenciales:

Usuario
```
root
```
Contraseña
```
admin
```

## 1. Crear una carpeta donde estará todo el proyecto.

```bash
app_poo_flask
```
## 2. Crear la siguiente estructura de archivos:
```bash
app_poo_flask/
├── app.py # Archivo principal de la aplicación
├── config.py # Configuración de la base de datos y otras variables
├── models.py # Definición de las clases modelo (POO para la DB)
├── controllers.py # Lógica de negocio y manejo de rutas
├── templates/ # Archivos HTML (interfaz gráfica)
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   └── dashboard.html
└── static/ # Archivos estáticos (CSS, JS, imágenes)
    └── css/
        └── style.css
```

## 3. Instalar bibliotecas:

```bash
pip install Flask Flask-SQLAlchemy Flask-Login PyMySQL
```

## 4. Crear la base de datos:
Asegúrate de tener un servidor MySQL funcionando y crea una base de datos.

```sql
CREATE DATABASE mi_app_db;
```

## 5. Código de la Aplicación

### 5.1 config.py (Archivo de Configuración)

```python
# config.py

import os

class Config:
    # Clave secreta para la seguridad de las sesiones de Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una_clave_secreta_muy_dificil_de_adivinar'

    # Configuración de la base de datos MySQL
    # Formato: mysql+pymysql://usuario:contraseña@host/nombre_db
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:admin@localhost/mi_app_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Desactiva el seguimiento de modificaciones de objetos
```
Nota: Es recomendable usar variables de entorno para SECRET_KEY y la contraseña de la base de datos en un entorno de producción. Por simplicidad, aquí lo ponemos directamente.

### 5.2 models.py (Clases Modelo)
Aquí definimos nuestras clases Python que representarán las tablas de la base de datos.

```python
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
```

### 5.3 controllers.py (Lógica de negocio y rutas)
Aquí definimos las funciones que manejan las rutas (URLs) de nuestra aplicación y la lógica de negocio asociada.

```python
# controllers.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

# Crea un Blueprint para organizar las rutas
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)

@main_bp.route('/')
def index():
    """Ruta de la página de inicio."""
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required # Esta ruta requiere que el usuario esté autenticado
def dashboard():
    """Ruta del panel de control del usuario."""
    return render_template('dashboard.html', user=current_user)

# Rutas de autenticación
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Ruta para el registro de nuevos usuarios."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Validaciones básicas
        if not username or not email or not password:
            flash('Por favor, completa todos los campos.', 'danger')
            return redirect(url_for('auth.register'))

        existing_user_username = User.query.filter_by(username=username).first()
        existing_user_email = User.query.filter_by(email=email).first()

        if existing_user_username:
            flash('El nombre de usuario ya existe.', 'danger')
            return redirect(url_for('auth.register'))
        if existing_user_email:
            flash('El correo electrónico ya está registrado.', 'danger')
            return redirect(url_for('auth.register'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registro exitoso. ¡Ahora puedes iniciar sesión!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar el usuario: {e}', 'danger')
            return redirect(url_for('auth.register'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Ruta para el inicio de sesión de usuarios."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'on'

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=remember_me)
            flash('¡Inicio de sesión exitoso!', 'success')
            # Redirige al usuario a la página que intentó acceder antes de iniciar sesión
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Nombre de usuario o contraseña incorrectos.', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required # Solo usuarios logeados pueden cerrar sesión
def logout():
    """Ruta para cerrar la sesión del usuario."""
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('main.index'))
```
### 5.4 app.py (Aplicación Principal)
Este es el archivo principal que inicializa Flask, conecta las extensiones y registra los Blueprints.

```python
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
```
## 6 templates/ (Archivos HTML para la interfaz)

### 6.1 templates/base.html
```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Mi Aplicación Flask{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav>
        <a href="{{ url_for('main.index') }}">Inicio</a>
        {% if current_user.is_authenticated %}
            <a href="{{ url_for('main.dashboard') }}">Dashboard</a>
            <a href="{{ url_for('auth.logout') }}">Cerrar Sesión ({{ current_user.username }})</a>
        {% else %}
            <a href="{{ url_for('auth.login') }}">Iniciar Sesión</a>
            <a href="{{ url_for('auth.register') }}">Registrarse</a>
        {% endif %}
    </nav>

    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <ul class="flashes">
                    {% for category, message in messages %}
                        <li class="{{ category }}">{{ message }}</li>
                    {% endfor %}
                </ul>
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </div>
</body>
</html>
```
### 6.2 templates.index.html
```html
{% extends "base.html" %}

{% block title %}Inicio - Mi Aplicación Flask{% endblock %}

{% block content %}
    <h1>Bienvenido a Mi Aplicación Flask con POO</h1>
    <p>Esta es la página de inicio. Explora la aplicación.</p>
    {% if not current_user.is_authenticated %}
        <p>Por favor, <a href="{{ url_for('auth.login') }}">inicia sesión</a> o <a href="{{ url_for('auth.register') }}">regístrate</a> para acceder a más funcionalidades.</p>
    {% endif %}
{% endblock %}
```
### 6.3 templates/register.html
```python
{% extends "base.html" %}

{% block title %}Registrarse{% endblock %}

{% block content %}
    <h1>Registrarse</h1>
    <form method="POST" action="{{ url_for('auth.register') }}">
        <label for="username">Nombre de Usuario:</label>
        <input type="text" id="username" name="username" required>
        <br>
        <label for="email">Correo Electrónico:</label>
        <input type="email" id="email" name="email" required>
        <br>
        <label for="password">Contraseña:</label>
        <input type="password" id="password" name="password" required>
        <br>
        <button type="submit">Registrarse</button>
    </form>
    <p>¿Ya tienes una cuenta? <a href="{{ url_for('auth.login') }}">Inicia sesión aquí</a>.</p>
{% endblock %}
```
### 6.4 templates/login.html
```html
{% extends "base.html" %}

{% block title %}Iniciar Sesión{% endblock %}

{% block content %}
    <h1>Iniciar Sesión</h1>
    <form method="POST" action="{{ url_for('auth.login') }}">
        <label for="username">Nombre de Usuario:</label>
        <input type="text" id="username" name="username" required>
        <br>
        <label for="password">Contraseña:</label>
        <input type="password" id="password" name="password" required>
        <br>
        <input type="checkbox" id="remember_me" name="remember_me">
        <label for="remember_me">Recordarme</label>
        <br>
        <button type="submit">Iniciar Sesión</button>
    </form>
    <p>¿No tienes una cuenta? <a href="{{ url_for('auth.register') }}">Regístrate aquí</a>.</p>
{% endblock %}
```
### 6.5 templates/dashbard.html
```html
{% extends "base.html" %}

{% block title %}Dashboard - Mi Aplicación Flask{% endblock %}

{% block content %}
    <h1>Bienvenido al Dashboard, {{ user.username }}!</h1>
    <p>Aquí puedes ver tu información personal o realizar acciones exclusivas para usuarios autenticados.</p>
    <p>Tu correo electrónico es: {{ user.email }}</p>
    <p><a href="{{ url_for('auth.logout') }}">Cerrar Sesión</a></p>
{% endblock %}
```
## 7 static/ (archivos css y js)

### 7.1 static/css/style.css
```css
/* static/css/style.css */

body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f4f4f4;
    color: #333;
}

nav {
    background-color: #333;
    color: white;
    padding: 1em;
    text-align: center;
}

nav a {
    color: white;
    text-decoration: none;
    margin: 0 15px;
}

nav a:hover {
    text-decoration: underline;
}

.container {
    max-width: 800px;
    margin: 20px auto;
    padding: 20px;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

h1 {
    color: #0056b3;
    text-align: center;
}

form label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}

form input[type="text"],
form input[type="email"],
form input[type="password"] {
    width: calc(100% - 22px);
    padding: 10px;
    margin-bottom: 15px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

form button {
    background-color: #007bff;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1em;
}

form button:hover {
    background-color: #0056b3;
}

.flashes {
    list-style: none;
    padding: 0;
    margin: 15px 0;
}

.flashes li {
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 4px;
    text-align: center;
}

.flashes .success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.flashes .danger {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

.flashes .info {
    background-color: #d1ecf1;
    color: #0c5460;
    border: 1px solid #bee5eb;
}

.flashes .warning {
    background-color: #fff3cd;
    color: #856404;
    border: 1px solid #ffeeba;
}
```
# 8 Ejecución
Guarda los archivos con la estructura de carpetas indicada.
Asegúrate de que tu servidor MySQL esté funcionando y que la base de datos mi_app_db y el usuario flask_user (con su contraseña) estén configurados como se mencionó en los "Pasos Previos".
Abre tu terminal en la raíz de la carpeta mi_app_flask_poo/.
Ejecuta el archivo app.py:

```bash
En el archivo app.py hacer PLAY con el botón
```
