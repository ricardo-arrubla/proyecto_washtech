from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import date
from sqlalchemy import or_, func

from models.washing_machine import WashingMachine
from models.reservation import Reservation
from models.user import User

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Lógica para mostrar dashboard según el rol
    user_role = current_user.role

    if user_role == 'cliente':
        return render_template('dashboard/client.html', user=current_user)

    # Para admin/superadmin calculamos estadísticas reales
    if user_role in ('admin', 'superadmin'):
        # Conteos básicos
        total_machines = WashingMachine.query.filter_by(is_active=True).count()
        operatives_count = WashingMachine.query.filter_by(operational_status='operativa', is_active=True).count()
        maintenance_count = WashingMachine.query.filter_by(operational_status='mantenimiento', is_active=True).count()
        inactive_count = WashingMachine.query.filter(or_(WashingMachine.operational_status == 'inactiva', WashingMachine.is_active == False)).count()

        # Reservas
        today = date.today()
        reservas_hoy = Reservation.query.filter_by(reservation_date=today, is_active=True).count()
        reservas_pendientes = Reservation.query.filter_by(status='pendiente', is_active=True).count()

        # Clientes activos
        clients_active = User.query.filter_by(role='cliente', is_active=True).count()

        return render_template('dashboard/admin.html', user=current_user,
                               total_machines=total_machines,
                               operatives_count=operatives_count,
                               maintenance_count=maintenance_count,
                               inactive_count=inactive_count,
                               reservas_hoy=reservas_hoy,
                               reservas_pendientes=reservas_pendientes,
                               clients_active=clients_active)

    return render_template('dashboard/client.html', user=current_user)