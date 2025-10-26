from database.connection import db
from datetime import datetime

class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    washing_machine_id = db.Column(db.Integer, db.ForeignKey('washing_machines.id'), nullable=False)
    availability = db.Column(db.Boolean, default=True)
    location = db.Column(db.String(100))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Inventory Machine {self.washing_machine_id} - Available: {self.availability}>'