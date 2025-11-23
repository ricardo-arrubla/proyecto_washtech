from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, current_user, login_required
import os

from config import Config
from database.connection import db
from models.user import User

def create_app():
    # Configurar Flask para servir archivos estáticos desde `views/static`
    # (las plantillas usan rutas como `/static/images/...` pero los archivos
    # están en `views/static/images/` en este proyecto)
    app = Flask(__name__, static_folder='views/static')
    app.config.from_object(Config)
    # Carpeta para subir imágenes (se guardarán en views/static/images)
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'images')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Registrar blueprints
    from controllers.auth_controller import auth_bp
    from controllers.dashboard_controller import dashboard_bp
    from controllers.reservation_controller import reservation_bp
    from controllers.admin_controller import admin_bp
    from controllers.catalog_controller import catalog_bp
    from controllers.report_controller import report_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(reservation_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(report_bp)
    
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