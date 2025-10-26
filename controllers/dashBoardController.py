from flask import Blueprint, render_template
from flask_login import login_required, current_user

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Lógica para mostrar dashboard según el rol
    user_role = current_user.role
    
    if user_role == 'cliente':
        return render_template('dashboard/client.html', user=current_user)
    elif user_role == 'admin':
        return render_template('dashboard/admin.html', user=current_user)
    elif user_role == 'superadmin':
        return render_template('dashboard/superadmin.html', user=current_user)
    
    return render_template('dashboard/client.html', user=current_user)