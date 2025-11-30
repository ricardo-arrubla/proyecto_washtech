from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse as url_parse

from database.connection import db
from models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, is_active=True).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('dashboard.index')
            return redirect(next_page)
        else:
            flash('Email o contraseña incorrectos', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        # Verificar si el usuario ya existe
        if User.query.filter_by(email=email).first():
            flash('El email ya está registrado', 'error')
            return render_template('auth/register.html')
        
        # Crear nuevo usuario
        new_user = User(
            name=name,
            email=email,
            phone=phone,
            address=address,
            role='cliente'
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Ver y editar el perfil del usuario actual"""
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        # Password change is handled via a separate flow
        current_user.name = name or current_user.name
        current_user.phone = phone or current_user.phone
        current_user.address = address or current_user.address

        db.session.commit()
        flash('Perfil actualizado correctamente', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html', user=current_user)


@auth_bp.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Formulario para cambiar la contraseña del usuario actual"""
    if request.method == 'POST':
        current_pwd = request.form.get('current_password')
        new_pwd = request.form.get('new_password')
        confirm_pwd = request.form.get('confirm_password')

        if not current_user.check_password(current_pwd):
            flash('La contraseña actual es incorrecta', 'error')
            return redirect(url_for('auth.change_password'))

        if not new_pwd or new_pwd != confirm_pwd:
            flash('La nueva contraseña y la confirmación no coinciden', 'error')
            return redirect(url_for('auth.change_password'))

        current_user.set_password(new_pwd)
        db.session.commit()
        flash('Contraseña actualizada correctamente', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/change_password.html')