from database.connection import db
from datetime import datetime

class Reservation(db.Model):
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    washing_machine_id = db.Column(db.Integer, db.ForeignKey('washing_machines.id'), nullable=False)
    reservation_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='pendiente')  # pendiente, confirmada, cancelada, completada
    total_payment = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con pagos
    payments = db.relationship('Payment', backref='reservation', lazy=True)
    
    def __repr__(self):
        return f'<Reservation {self.id} - User {self.user_id}>'