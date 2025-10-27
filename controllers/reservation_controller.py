from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, time
from sqlalchemy import and_

from database.connection import db
from models.reservation import Reservation
from models.washing_machine import WashingMachine
from models.payment import Payment

reservation_bp = Blueprint('reservation', __name__, url_prefix='/reservas')

@reservation_bp.route('/')
@login_required
def index():
    """Listar reservas del usuario actual"""
    if current_user.role == 'cliente':
        reservations = Reservation.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).order_by(Reservation.reservation_date.desc()).all()
    else:
        # Admin ve todas las reservas
        reservations = Reservation.query.filter_by(
            is_active=True
        ).order_by(Reservation.reservation_date.desc()).all()
    
    return render_template('reservation/list.html', reservations=reservations)

@reservation_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def create():
    """Crear nueva reserva"""
    machine_id = request.args.get('machine_id', type=int)
    date_str = request.args.get('date', '')
    
    if request.method == 'GET':
        # Cargar datos para el formulario
        machines = WashingMachine.query.filter_by(
            is_active=True,
            operational_status='operativa'
        ).all()
        
        selected_machine = None
        if machine_id:
            selected_machine = WashingMachine.query.get(machine_id)
        
        return render_template('reservation/create.html', 
                             machines=machines,
                             selected_machine=selected_machine,
                             selected_date=date_str)
    
    # POST - Procesar reserva
    machine_id = request.form.get('machine_id', type=int)
    reservation_date = request.form.get('reservation_date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    
    # Validaciones
    if not all([machine_id, reservation_date, start_time, end_time]):
        flash('Todos los campos son obligatorios', 'error')
        return redirect(url_for('reservation.create'))
    
    # Convertir fecha y horas
    try:
        res_date = datetime.strptime(reservation_date, '%Y-%m-%d').date()
        start = datetime.strptime(start_time, '%H:%M').time()
        end = datetime.strptime(end_time, '%H:%M').time()
    except ValueError:
        flash('Formato de fecha u hora inválido', 'error')
        return redirect(url_for('reservation.create'))
    
    # Verificar disponibilidad
    existing_reservation = Reservation.query.filter(
        and_(
            Reservation.washing_machine_id == machine_id,
            Reservation.reservation_date == res_date,
            Reservation.status.in_(['pendiente', 'confirmada']),
            Reservation.is_active == True
        )
    ).first()
    
    if existing_reservation:
        flash('La lavadora no está disponible en esa fecha', 'error')
        return redirect(url_for('reservation.create', machine_id=machine_id))
    
    # Calcular precio (ejemplo: $50,000 por día)
    total_payment = 50000.0
    
    # Crear reserva
    new_reservation = Reservation(
        user_id=current_user.id,
        washing_machine_id=machine_id,
        reservation_date=res_date,
        start_time=start,
        end_time=end,
        status='pendiente',
        total_payment=total_payment
    )
    
    db.session.add(new_reservation)
    db.session.commit()
    
    flash('Reserva creada exitosamente', 'success')
    return redirect(url_for('reservation.detail', id=new_reservation.id))

@reservation_bp.route('/<int:id>')
@login_required
def detail(id):
    """Ver detalle de reserva"""
    reservation = Reservation.query.get_or_404(id)
    
    # Verificar permisos
    if current_user.role == 'cliente' and reservation.user_id != current_user.id:
        flash('No tienes permisos para ver esta reserva', 'error')
        return redirect(url_for('reservation.index'))
    
    return render_template('reservation/detail.html', reservation=reservation)

@reservation_bp.route('/<int:id>/cancelar', methods=['POST'])
@login_required
def cancel(id):
    """Cancelar reserva"""
    reservation = Reservation.query.get_or_404(id)
    
    # Verificar permisos
    if current_user.role == 'cliente' and reservation.user_id != current_user.id:
        flash('No tienes permisos para cancelar esta reserva', 'error')
        return redirect(url_for('reservation.index'))
    
    # Solo se pueden cancelar reservas pendientes
    if reservation.status not in ['pendiente']:
        flash('No se puede cancelar esta reserva', 'error')
        return redirect(url_for('reservation.detail', id=id))
    
    reservation.status = 'cancelada'
    db.session.commit()
    
    flash('Reserva cancelada exitosamente', 'success')
    return redirect(url_for('reservation.index'))