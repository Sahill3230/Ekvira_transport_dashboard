from datetime import datetime
from app.models import db

class Maintenance(db.Model):
    __tablename__ = 'maintenance'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    service_date = db.Column(db.Date, nullable=False)
    next_service_date = db.Column(db.Date, nullable=False)
    tyre_change = db.Column(db.Boolean, default=False)
    oil_change = db.Column(db.Boolean, default=False)
    battery_change = db.Column(db.Boolean, default=False)
    service_cost = db.Column(db.Numeric(10, 2), nullable=False)
    workshop_name = db.Column(db.String(150))
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Maintenance for Vehicle {self.vehicle_id} on {self.service_date}>"
