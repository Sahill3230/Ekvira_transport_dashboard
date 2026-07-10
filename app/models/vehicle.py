from datetime import datetime
from app.models import db

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    vehicle_name = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    registration_number = db.Column(db.String(50), unique=True, nullable=False)
    capacity = db.Column(db.Numeric(5, 2), nullable=False) # in tons
    insurance_date = db.Column(db.Date, nullable=False)
    fitness_date = db.Column(db.Date, nullable=False)
    puc_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(25), nullable=False, default='Idle')  # 'Active', 'Idle', 'Maintenance'
    current_latitude = db.Column(db.Numeric(10, 8), default=22.9734) # Default to Central India coal region
    current_longitude = db.Column(db.Numeric(11, 8), default=78.6569)
    odometer = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)
    fuel_type = db.Column(db.String(20), nullable=False, default='Diesel')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key to driver
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id', name='fk_vehicle_driver'), unique=True, nullable=True)
    
    # Establish relationship to Driver
    driver = db.relationship('Driver', foreign_keys=[driver_id], post_update=True, backref=db.backref('assigned_vehicle_backref', uselist=False))
    
    # Establish helper relationships for listings
    trips = db.relationship('Trip', backref='vehicle', lazy=True, cascade="all, delete-orphan")
    maintenance_records = db.relationship('Maintenance', backref='vehicle', lazy=True, cascade="all, delete-orphan")
    fuel_records = db.relationship('Fuel', backref='vehicle', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Vehicle {self.vehicle_number} - Status: {self.status}>"
