from flask import Blueprint

reservation_bp = Blueprint('reservation', __name__, url_prefix='/reservation')

@reservation_bp.route('/')
def index():
    return "Sistema de reservas - En desarrollo"