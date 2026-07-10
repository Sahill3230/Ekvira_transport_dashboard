from datetime import datetime
from app.models import db

class Fuel(db.Model):
    __tablename__ = 'fuel'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    fuel_filled = db.Column(db.Numeric(10, 2), nullable=False) # in liters
    price = db.Column(db.Numeric(10, 2), nullable=False) # price per liter
    mileage = db.Column(db.Numeric(5, 2), nullable=True) # calculated km/l
    fuel_station = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Fuel Filled {self.fuel_filled}L for Vehicle {self.vehicle_id} on {self.date}>"
