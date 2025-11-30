from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import and_, or_
from datetime import datetime, date

from database.connection import db
from models.washing_machine import WashingMachine
from models.inventory import Inventory
from models.reservation import Reservation

catalog_bp = Blueprint('catalog', __name__, url_prefix='/catalogo')

def extract_capacity_number(capacity_str):
    """Extrae el número de kg de una cadena de capacidad (ej: '15 kg' -> 15)"""
    try:
        return float(capacity_str.split()[0])
    except (ValueError, IndexError):
        return None

@catalog_bp.route('/')
def index():
    """Catálogo público de lavadoras"""
    # Obtener parámetros de búsqueda
    search = request.args.get('search', '')
    capacity_range = request.args.get('capacity', '')  # Rango: 'hasta_10', '10_15', '15_20', 'mas_20'
    status = request.args.get('status', '')
    
    # Query base
    query = WashingMachine.query.filter_by(is_active=True)
    
    # Aplicar filtros
    if search:
        query = query.filter(
            or_(
                WashingMachine.model.ilike(f'%{search}%'),
                WashingMachine.description.ilike(f'%{search}%')
            )
        )
    
    if status:
        query = query.filter(WashingMachine.operational_status == status)
    
    machines = query.all()
    
    # Aplicar filtro de rango de capacidad en memoria (post-query)
    if capacity_range:
        filtered_machines = []
        for machine in machines:
            capacity_num = extract_capacity_number(machine.capacity)
            if capacity_num is None:
                continue
            
            if capacity_range == 'hasta_10' and capacity_num <= 10:
                filtered_machines.append(machine)
            elif capacity_range == '10_15' and 10 < capacity_num <= 15:
                filtered_machines.append(machine)
            elif capacity_range == '15_20' and 15 < capacity_num <= 20:
                filtered_machines.append(machine)
            elif capacity_range == 'mas_20' and capacity_num > 20:
                filtered_machines.append(machine)
        
        machines = filtered_machines
    
    return render_template('catalog/index.html', 
                         machines=machines,
                         search=search,
                         capacity_range=capacity_range,
                         status=status)

@catalog_bp.route('/lavadora/<int:id>')
def detail(id):
    """Detalle de una lavadora"""
    machine = WashingMachine.query.get_or_404(id)
    
    # Verificar disponibilidad
    available = False
    if machine.inventory and machine.inventory.availability and machine.operational_status == 'operativa':
        available = True
    
    return render_template('catalog/detail.html', machine=machine, available=available)

@catalog_bp.route('/disponibilidad')
def check_availability():
    """Consultar disponibilidad por fecha"""
    reservation_date = request.args.get('date')
    
    if not reservation_date:
        return render_template('catalog/availability.html')
    
    try:
        check_date = datetime.strptime(reservation_date, '%Y-%m-%d').date()
    except ValueError:
        return render_template('catalog/availability.html', error='Fecha inválida')
    
    # Obtener lavadoras operativas
    all_machines = WashingMachine.query.filter_by(
        is_active=True,
        operational_status='operativa'
    ).all()
    
    # Filtrar las que NO tienen reservas ese día
    available_machines = []
    for machine in all_machines:
        reservations = Reservation.query.filter(
            and_(
                Reservation.washing_machine_id == machine.id,
                Reservation.reservation_date == check_date,
                Reservation.status.in_(['pendiente', 'confirmada']),
                Reservation.is_active == True
            )
        ).all()
        
        if not reservations:
            available_machines.append(machine)
    
    return render_template('catalog/availability.html',
                         machines=available_machines,
                         date=reservation_date)

@catalog_bp.route('/api/disponibilidad/<int:machine_id>')
def api_check_machine_availability(machine_id):
    """API para verificar disponibilidad de una lavadora específica"""
    date_str = request.args.get('date')
    
    if not date_str:
        return jsonify({'error': 'Fecha requerida'}), 400
    
    try:
        check_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido'}), 400
    
    machine = WashingMachine.query.get_or_404(machine_id)
    
    # Verificar estado operativo
    if machine.operational_status != 'operativa':
        return jsonify({
            'available': False,
            'reason': 'Lavadora en mantenimiento'
        })
    
    # Verificar reservas
    reservations = Reservation.query.filter(
        and_(
            Reservation.washing_machine_id == machine_id,
            Reservation.reservation_date == check_date,
            Reservation.status.in_(['pendiente', 'confirmada']),
            Reservation.is_active == True
        )
    ).all()
    
    if reservations:
        return jsonify({
            'available': False,
            'reason': 'Lavadora reservada ese día',
            'reservations': len(reservations)
        })
    
    return jsonify({
        'available': True,
        'machine': {
            'id': machine.id,
            'model': machine.model,
            'capacity': machine.capacity
        }
    })