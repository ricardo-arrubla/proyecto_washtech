from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from functools import wraps

from database.connection import db
from models.washing_machine import WashingMachine
from models.inventory import Inventory
from models.user import User
from models.reservation import Reservation
from sqlalchemy.orm import joinedload

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Permisos de extensiones de imagen
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        # Soporte para subida de archivo o usar icono por defecto
        use_default = request.form.get('use_default') == 'on'
        image_file = request.files.get('image_file')
        description = request.form.get('description')
        location = request.form.get('location')
        
        # Crear lavadora
        # If image_url is empty string, store None so the model/DB default applies
        # Inicialmente no asignamos image_url para que el default del modelo aplique
        new_machine = WashingMachine(
            model=model,
            capacity=capacity,
            operational_status=operational_status,
            acquisition_date=datetime.strptime(acquisition_date, '%Y-%m-%d').date() if acquisition_date else None,
            image_url=None,
            description=description
        )
        
        db.session.add(new_machine)
        db.session.flush()  # Para obtener el ID

        # Guardar archivo si se subió y no se eligió el icono por defecto
        if not use_default and image_file and image_file.filename and allowed_file(image_file.filename):
            filename = f"{new_machine.id}_" + secure_filename(image_file.filename)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            image_file.save(save_path)
            new_machine.image_url = f"/static/images/{filename}"
        
        # Crear registro en inventario
        # Si la lavadora no está operativa, marcar como no disponible automáticamente
        initial_availability = True if operational_status == 'operativa' else False
        inventory = Inventory(
            washing_machine_id=new_machine.id,
            availability=initial_availability,
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
        # Manejo de imagen: subir archivo nuevo o usar icono por defecto
        use_default = request.form.get('use_default') == 'on'
        image_file = request.files.get('image_file')
        if use_default:
            machine.image_url = None
        elif image_file and image_file.filename and allowed_file(image_file.filename):
            filename = f"{machine.id}_" + secure_filename(image_file.filename)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            image_file.save(save_path)
            machine.image_url = f"/static/images/{filename}"
        machine.description = request.form.get('description')
        
        # Actualizar inventario
        if machine.inventory:
            machine.inventory.location = request.form.get('location')
            # Si el estado operativo es mantenimiento o inactiva, forzamos no disponible
            if machine.operational_status in ('mantenimiento', 'inactiva'):
                machine.inventory.availability = False
            else:
                # Si está operativa, respetamos la selección del formulario
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


@admin_bp.route('/usuarios/<int:id>')
@login_required
@admin_required
def view_user(id):
    """Ver detalle de un usuario: máquinas reservadas y historial de reservas"""
    user = User.query.get_or_404(id)
    # Obtener reservas (incluye históricas). Usar joinedload para cargar lavadora relacionada.
    reservations = Reservation.query.filter(Reservation.user_id == user.id).options(
        joinedload(Reservation.washing_machine)
    ).order_by(Reservation.created_at.desc()).all()

    # Conjunto de máquinas reservadas por el usuario (únicas)
    machines = []
    seen = set()
    for r in reservations:
        if r.washing_machine and r.washing_machine.id not in seen:
            machines.append(r.washing_machine)
            seen.add(r.washing_machine.id)

    return render_template('admin/users/view.html', user=user, reservations=reservations, machines=machines)

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
    
    if new_role in ['cliente', 'admin', 'superadmin', 'operador']:
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

# ==================== GESTIÓN DE PENDIENTES ====================

@admin_bp.route('/pendientes')
@login_required
@admin_required
def pending_reservations():
    """Ver todas las reservas pendientes sin asignar"""
    from datetime import date
    today = date.today()
    
    # Reservas pendientes sin operador asignado
    unassigned_pending = Reservation.query.filter(
        Reservation.status == 'pendiente',
        Reservation.assigned_operator_id == None,
        Reservation.is_active == True
    ).order_by(Reservation.reservation_date.asc(), Reservation.start_time.asc()).all()
    
    # Reservas pendientes asignadas (para ver distribución)
    assigned_pending = Reservation.query.filter(
        Reservation.status == 'pendiente',
        Reservation.assigned_operator_id != None,
        Reservation.is_active == True
    ).order_by(Reservation.reservation_date.asc(), Reservation.start_time.asc()).all()
    
    # Obtener operadores disponibles
    operators = User.query.filter_by(role='operador', is_active=True).all()

    # Todas las reservas pendientes (asignadas y sin asignar)
    pending_all = unassigned_pending + assigned_pending

    # Lista de lavadoras que tienen alguna reserva pendiente (únicas)
    pending_machines = []
    machine_counts = {}
    seen = set()
    for r in pending_all:
        # Aseguramos que la lavadora esté cargada
        wm = r.washing_machine
        if not wm:
            continue
        # contar reservas por máquina
        machine_counts[wm.id] = machine_counts.get(wm.id, 0) + 1
        if wm.id not in seen:
            pending_machines.append(wm)
            seen.add(wm.id)

    return render_template('admin/pending_reservations.html', 
                         unassigned_pending=unassigned_pending,
                         assigned_pending=assigned_pending,
                         operators=operators,
                         pending_machines=pending_machines,
                         machine_counts=machine_counts)

@admin_bp.route('/pendientes/<int:id>/asignar', methods=['POST'])
@login_required
@admin_required
def assign_operator(id):
    """Asignar operador a una reserva pendiente"""
    reservation = Reservation.query.get_or_404(id)
    operator_id = request.form.get('operator_id')
    
    # Verificar que la reserva esté pendiente
    if reservation.status != 'pendiente':
        flash('Solo puedes asignar operadores a reservas pendientes', 'error')
        return redirect(url_for('admin.pending_reservations'))
    
    # Verificar que el operador existe y es válido
    operator = User.query.get_or_404(int(operator_id))
    if operator.role != 'operador' or not operator.is_active:
        flash('Operador inválido', 'error')
        return redirect(url_for('admin.pending_reservations'))
    
    # Asignar operador
    reservation.assigned_operator_id = operator.id
    db.session.commit()
    
    flash(f'Reserva #{reservation.id} asignada a {operator.name}', 'success')
    return redirect(url_for('admin.pending_reservations'))

@admin_bp.route('/pendientes/<int:id>/desasignar', methods=['POST'])
@login_required
@admin_required
def unassign_operator(id):
    """Desasignar operador de una reserva pendiente"""
    reservation = Reservation.query.get_or_404(id)
    
    # Verificar que la reserva esté pendiente
    if reservation.status != 'pendiente':
        flash('Solo puedes desasignar operadores de reservas pendientes', 'error')
        return redirect(url_for('admin.pending_reservations'))
    
    # Desasignar operador
    operator_name = reservation.assigned_operator.name if reservation.assigned_operator else 'N/A'
    reservation.assigned_operator_id = None
    db.session.commit()
    
    flash(f'Reserva #{reservation.id} desasignada de {operator_name}', 'success')
    return redirect(url_for('admin.pending_reservations'))