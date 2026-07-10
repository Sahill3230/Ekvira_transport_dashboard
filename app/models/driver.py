from datetime import datetime
from app.models import db

class Driver(db.Model):
    __tablename__ = 'drivers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    license_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    license_expiry = db.Column(db.Date, nullable=False)
    address = db.Column(db.Text)
    aadhaar_number = db.Column(db.String(12), unique=True, nullable=False, index=True)
    joining_date = db.Column(db.Date, nullable=False)
    salary = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Active')  # 'Active', 'Inactive', 'On Trip'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Self-assignment link to vehicle to prevent circular dependencies in relationships:
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id', name='fk_driver_vehicle'), unique=True, nullable=True)
    
    # We will declare relationships in Vehicle model or here. Let's declare it in Vehicle and use foreign_keys argument.
    
    def __repr__(self):
        return f"<Driver {self.name} - Status: {self.status}>"
