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
        # Estadísticas específicas para el cliente actual
        # Reservas activas (pendiente o confirmada)
        reservas_activas = Reservation.query.filter(
            Reservation.user_id == current_user.id,
            Reservation.is_active == True,
            Reservation.status.in_(['pendiente', 'confirmada'])
        ).count()

        # Total de alquileres (historial)
        total_alquileres = Reservation.query.filter_by(user_id=current_user.id).count()

        # Próxima reserva (la más cercana a hoy)
        today = date.today()
        next_reservation = Reservation.query.filter(
            Reservation.user_id == current_user.id,
            Reservation.is_active == True,
            Reservation.reservation_date >= today
        ).order_by(Reservation.reservation_date.asc(), Reservation.start_time.asc()).first()

        # Reservas recientes (últimas 5)
        recent_reservations = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.created_at.desc()).limit(5).all()

        return render_template('dashBoard/client.html', user=current_user,
                               reservas_activas=reservas_activas,
                               total_alquileres=total_alquileres,
                               next_reservation=next_reservation,
                               recent_reservations=recent_reservations)

    # Para operador mostrar dashboard específico
    if user_role == 'operador':
        from flask import redirect, url_for
        return redirect(url_for('operator.dashboard'))

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

        return render_template('dashBoard/admin.html', user=current_user,
                               total_machines=total_machines,
                               operatives_count=operatives_count,
                               maintenance_count=maintenance_count,
                               inactive_count=inactive_count,
                               reservas_hoy=reservas_hoy,
                               reservas_pendientes=reservas_pendientes,
                               clients_active=clients_active)

    return render_template('dashBoard/client.html', user=current_user)