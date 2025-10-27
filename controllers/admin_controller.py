from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from functools import wraps

from database.connection import db
from models.washing_machine import WashingMachine
from models.inventory import Inventory
from models.user import User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Decorador para verificar rol de admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'superadmin']:
            flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== CRUD LAVADORAS ====================

@admin_bp.route('/lavadoras')
@login_required
@admin_required
def list_washing_machines():
    """Listar todas las lavadoras"""
    machines = WashingMachine.query.filter_by(is_active=True).all()
    return render_template('admin/washing_machines/list.html', machines=machines)

@admin_bp.route('/lavadoras/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def create_washing_machine():
    """Crear nueva lavadora"""
    if request.method == 'POST':
        model = request.form.get('model')
        capacity = request.form.get('capacity')
        operational_status = request.form.get('operational_status', 'operativa')
        acquisition_date = request.form.get('acquisition_date')
        image_url = request.form.get('image_url')
        description = request.form.get('description')
        location = request.form.get('location')
        
        # Crear lavadora
        new_machine = WashingMachine(
            model=model,
            capacity=capacity,
            operational_status=operational_status,
            acquisition_date=datetime.strptime(acquisition_date, '%Y-%m-%d').date() if acquisition_date else None,
            image_url=image_url,
            description=description
        )
        
        db.session.add(new_machine)
        db.session.flush()  # Para obtener el ID
        
        # Crear registro en inventario
        inventory = Inventory(
            washing_machine_id=new_machine.id,
            availability=True,
            location=location
        )
        
        db.session.add(inventory)
        db.session.commit()
        
        flash(f'Lavadora {model} creada exitosamente', 'success')
        return redirect(url_for('admin.list_washing_machines'))
    
    return render_template('admin/washing_machines/create.html')

@admin_bp.route('/lavadoras/<int:id>')
@login_required
@admin_required
def view_washing_machine(id):
    """Ver detalles de lavadora"""
    machine = WashingMachine.query.get_or_404(id)
    return render_template('admin/washing_machines/view.html', machine=machine)

@admin_bp.route('/lavadoras/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_washing_machine(id):
    """Editar lavadora"""
    machine = WashingMachine.query.get_or_404(id)
    
    if request.method == 'POST':
        machine.model = request.form.get('model')
        machine.capacity = request.form.get('capacity')
        machine.operational_status = request.form.get('operational_status')
        acquisition_date = request.form.get('acquisition_date')
        if acquisition_date:
            machine.acquisition_date = datetime.strptime(acquisition_date, '%Y-%m-%d').date()
        machine.image_url = request.form.get('image_url')
        machine.description = request.form.get('description')
        
        # Actualizar inventario
        if machine.inventory:
            machine.inventory.location = request.form.get('location')
            machine.inventory.availability = request.form.get('availability') == 'true'
        
        db.session.commit()
        flash(f'Lavadora {machine.model} actualizada exitosamente', 'success')
        return redirect(url_for('admin.list_washing_machines'))
    
    return render_template('admin/washing_machines/edit.html', machine=machine)

@admin_bp.route('/lavadoras/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def delete_washing_machine(id):
    """Eliminar lavadora (borrado lógico)"""
    machine = WashingMachine.query.get_or_404(id)
    machine.is_active = False
    if machine.inventory:
        machine.inventory.is_active = False
    db.session.commit()
    flash(f'Lavadora {machine.model} eliminada exitosamente', 'success')
    return redirect(url_for('admin.list_washing_machines'))

# ==================== GESTIÓN DE USUARIOS ====================

@admin_bp.route('/usuarios')
@login_required
@admin_required
def list_users():
    """Listar todos los usuarios"""
    users = User.query.filter_by(is_active=True).all()
    return render_template('admin/users/list.html', users=users)

@admin_bp.route('/usuarios/<int:id>/cambiar-rol', methods=['POST'])
@login_required
@admin_required
def change_user_role(id):
    """Cambiar rol de usuario"""
    if current_user.role != 'superadmin':
        flash('Solo el superadmin puede cambiar roles', 'error')
        return redirect(url_for('admin.list_users'))
    
    user = User.query.get_or_404(id)
    new_role = request.form.get('role')
    
    if new_role in ['cliente', 'admin', 'superadmin']:
        user.role = new_role
        db.session.commit()
        flash(f'Rol de {user.name} actualizado a {new_role}', 'success')
    else:
        flash('Rol inválido', 'error')
    
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/usuarios/<int:id>/desactivar', methods=['POST'])
@login_required
@admin_required
def deactivate_user(id):
    """Desactivar usuario"""
    user = User.query.get_or_404(id)
    user.is_active = False
    db.session.commit()
    flash(f'Usuario {user.name} desactivado', 'success')
    return redirect(url_for('admin.list_users'))