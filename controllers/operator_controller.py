from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from datetime import date

from database.connection import db
from models.reservation import Reservation
from models.washing_machine import WashingMachine

operator_bp = Blueprint('operator', __name__, url_prefix='/operator')

# Decorador para verificar rol de operador
def operator_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['operador', 'admin', 'superadmin']:
            flash('Acceso denegado. Se requieren permisos de operador.', 'error')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== DASHBOARD OPERADOR ====================

@operator_bp.route('/dashboard')
@login_required
@operator_required
def dashboard():
    """Dashboard del operador con reservas pendientes asignadas"""
    # Obtener reservas pendientes asignadas al operador actual
    pending_reservations = Reservation.query.filter(
        Reservation.assigned_operator_id == current_user.id,
        Reservation.status == 'pendiente',
        Reservation.is_active == True
    ).order_by(Reservation.reservation_date.asc(), Reservation.start_time.asc()).all()
    
    # Contar reservas entregadas hoy
    today = date.today()
    delivered_today = Reservation.query.filter(
        Reservation.assigned_operator_id == current_user.id,
        Reservation.status == 'entregado',
        Reservation.reservation_date == today
    ).count()
    
    # Total de reservas completadas por el operador
    total_completed = Reservation.query.filter(
        Reservation.assigned_operator_id == current_user.id,
        Reservation.status == 'entregado'
    ).count()
    
    # Reservas en proceso (confirmadas y asignadas)
    in_progress = Reservation.query.filter(
        Reservation.assigned_operator_id == current_user.id,
        Reservation.status == 'confirmada'
    ).count()
    
    return render_template('dashBoard/operator.html', 
                         user=current_user,
                         pending_reservations=pending_reservations,
                         delivered_today=delivered_today,
                         total_completed=total_completed,
                         in_progress=in_progress)

# ==================== CAMBIAR ESTADO DE RESERVA ====================

@operator_bp.route('/reserva/<int:id>/entregar', methods=['POST'])
@login_required
@operator_required
def deliver_reservation(id):
    """Cambiar estado de reserva a entregado"""
    reservation = Reservation.query.get_or_404(id)
    
    # Verificar que la reserva esté asignada al operador actual
    if reservation.assigned_operator_id != current_user.id:
        flash('No tienes permiso para modificar esta reserva', 'error')
        return redirect(url_for('operator.dashboard'))
    
    # Verificar que la reserva esté en estado pendiente
    if reservation.status != 'pendiente':
        flash('Solo puedes entregar reservas en estado pendiente', 'error')
        return redirect(url_for('operator.dashboard'))
    
    # Cambiar estado a entregado
    reservation.status = 'entregado'
    db.session.commit()
    
    flash(f'Lavadora {reservation.washing_machine.model} entregada correctamente', 'success')
    return redirect(url_for('operator.dashboard'))

@operator_bp.route('/reserva/<int:id>/cancelar', methods=['POST'])
@login_required
@operator_required
def cancel_reservation(id):
    """Cancelar una reserva pendiente (solo operador que la tiene asignada)"""
    reservation = Reservation.query.get_or_404(id)
    
    # Verificar que la reserva esté asignada al operador actual
    if reservation.assigned_operator_id != current_user.id:
        flash('No tienes permiso para cancelar esta reserva', 'error')
        return redirect(url_for('operator.dashboard'))
    
    # Verificar que la reserva esté en estado pendiente o confirmada
    if reservation.status not in ['pendiente', 'confirmada']:
        flash('No puedes cancelar reservas en este estado', 'error')
        return redirect(url_for('operator.dashboard'))
    
    # Cambiar estado a cancelada
    reservation.status = 'cancelada'
    reservation.assigned_operator_id = None
    db.session.commit()
    
    flash(f'Reserva cancelada correctamente', 'warning')
    return redirect(url_for('operator.dashboard'))

# ==================== VER DETALLE DE RESERVA ====================

@operator_bp.route('/reserva/<int:id>')
@login_required
@operator_required
def view_reservation(id):
    """Ver detalles de una reserva asignada"""
    reservation = Reservation.query.get_or_404(id)
    
    # Verificar que la reserva esté asignada al operador actual
    if reservation.assigned_operator_id != current_user.id:
        flash('No tienes permiso para ver esta reserva', 'error')
        return redirect(url_for('operator.dashboard'))
    
    return render_template('operator/reservation_detail.html', reservation=reservation)
