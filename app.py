from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, current_user, login_required
import os

from config import Config
from database.connection import db
from models.user import User
from models.washing_machine import WashingMachine


def create_app():
    """Factory function para crear la aplicación Flask"""
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
    from controllers.operator_controller import operator_bp
    from controllers.catalog_controller import catalog_bp
    from controllers.report_controller import report_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(reservation_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(operator_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(report_bp)
    
    # Ruta principal
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        # Contar lavadoras activas y pasarlo a la plantilla
        try:
            washing_count = WashingMachine.query.filter_by(is_active=True).count()
        except Exception:
            # Si hay problema con la BD (por ejemplo en primera ejecución), usar 0
            washing_count = 0
        return render_template('index.html', washing_count=washing_count)
    
    return app


# Crear instancia global de la aplicación
# Esta es la que Gunicorn importará cuando ejecute: gunicorn app:app
app = create_app()

# Crear tablas automáticamente cuando se importa el módulo (Gunicorn lo hará)
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    # Punto de entrada para desarrollo local (python run.py)
    with app.app_context():
        print('✅ Tablas de base de datos verificadas/creadas')
    
    # Ejecutar servidor de desarrollo
    # - debug=True: recarga automática al cambiar código
    # - host='0.0.0.0': accesible desde cualquier interfaz de red
    # - port=5000: puerto por defecto de Flask
    print('🚀 Iniciando WashTech en http://127.0.0.1:5000')
    app.run(debug=True, host='0.0.0.0', port=5000)