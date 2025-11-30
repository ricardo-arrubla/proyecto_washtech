from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database.connection import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    role = db.Column(db.String(20), default='cliente')  # cliente, admin, superadmin, operador
    is_active = db.Column(db.Boolean, default=True)
    registration_date = db.Column(db.DateTime, default=db.func.now())
    
    # Relaciones
    reservations = db.relationship('Reservation', foreign_keys='Reservation.user_id', backref='user', lazy=True)
    # Operador puede tener muchas reservas asignadas
    assigned_reservations = db.relationship('Reservation', foreign_keys='Reservation.assigned_operator_id', backref='assigned_operator', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'