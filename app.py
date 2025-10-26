from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, current_user, login_required
import os

from config import Config
from database.connection import db
from models.user import User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Registrar blueprints
    from controllers.auth_controller import auth_bp
    from controllers.dashboard_controller import dashboard_bp
    from controllers.reservation_controller import reservation_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(reservation_bp)
    
    # Ruta principal
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return render_template('index.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)