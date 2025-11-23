from flask import Blueprint, render_template, request, Response
from flask_login import login_required, current_user
from database.connection import db
from models.reservation import Reservation
from models.user import User
from models.washing_machine import WashingMachine
import csv
import io
from datetime import datetime

report_bp = Blueprint('report', __name__, url_prefix='/reportes')


@report_bp.route('/')
@login_required
def index():
    # Page with basic reports / links
    return render_template('admin/reports/index.html')


@report_bp.route('/reservas.csv')
@login_required
def reservas_csv():
    """Genera un CSV con las reservas. Parámetros opcionales:
    - start_date: YYYY-MM-DD
    - end_date: YYYY-MM-DD
    - status: pendiente|confirmada|cancelada|completada
    - user_id: id numérico de usuario
    """
    q = Reservation.query.join(User, Reservation.user_id == User.id).join(
        WashingMachine, Reservation.washing_machine_id == WashingMachine.id
    )

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    status = request.args.get('status')
    user_id = request.args.get('user_id')

    # Aplicar filtros si vienen
    if start_date:
        try:
            sd = datetime.strptime(start_date, '%Y-%m-%d').date()
            q = q.filter(Reservation.reservation_date >= sd)
        except Exception:
            pass
    if end_date:
        try:
            ed = datetime.strptime(end_date, '%Y-%m-%d').date()
            q = q.filter(Reservation.reservation_date <= ed)
        except Exception:
            pass
    if status:
        q = q.filter(Reservation.status == status)
    if user_id:
        try:
            uid = int(user_id)
            q = q.filter(Reservation.user_id == uid)
        except Exception:
            pass

    rows = q.all()

    si = io.StringIO()
    writer = csv.writer(si)

    # Cabeceras
    writer.writerow([
        'id', 'user_id', 'user_email', 'machine_id', 'machine_model',
        'reservation_date', 'start_time', 'end_time', 'status', 'total_payment'
    ])

    for r in rows:
        writer.writerow([
            r.id,
            r.user.id if r.user else '',
            r.user.email if r.user else '',
            r.washing_machine.id if r.washing_machine else '',
            r.washing_machine.model if r.washing_machine else '',
            r.reservation_date.isoformat() if r.reservation_date else '',
            r.start_time.strftime('%H:%M:%S') if r.start_time else '',
            r.end_time.strftime('%H:%M:%S') if r.end_time else '',
            r.status,
            f"{(r.total_payment or 0):.2f}"
        ])

    output = si.getvalue()
    si.close()

    filename = f"reservas_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(output, mimetype='text/csv', headers={
        'Content-Disposition': f'attachment; filename={filename}'
    })
