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