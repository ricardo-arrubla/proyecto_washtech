from database.connection import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservations.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # efectivo, transferencia, tarjeta
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_status = db.Column(db.String(20), default='pendiente')  # pendiente, completado, fallido
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Payment {self.id} - Reservation {self.reservation_id}>'