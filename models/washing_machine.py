from database.connection import db

class WashingMachine(db.Model):
    __tablename__ = 'washing_machines'
    
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.String(50), nullable=False)  # ej: "7 kg"
    operational_status = db.Column(db.String(20), default='operativa')  # operativa, mantenimiento, inactiva
    acquisition_date = db.Column(db.Date)
    image_url = db.Column(db.String(200))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relaciones
    reservations = db.relationship('Reservation', backref='washing_machine', lazy=True)
    inventory = db.relationship('Inventory', backref='washing_machine', uselist=False)
    
    def __repr__(self):
        return f'<WashingMachine {self.model}>'