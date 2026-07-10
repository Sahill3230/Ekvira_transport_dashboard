from datetime import datetime
from app.models import db

class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False) # 'Diesel', 'Driver Salary', 'Toll', 'Repair', 'Maintenance', 'Miscellaneous'
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    description = db.Column(db.Text)
    
    # Optional relation identifiers
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=True)
    maintenance_id = db.Column(db.Integer, db.ForeignKey('maintenance.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Optional relationships to help fetch related items easily
    vehicle = db.relationship('Vehicle', backref=db.backref('expenses', lazy=True))
    trip = db.relationship('Trip', backref=db.backref('expenses', lazy=True))
    maintenance = db.relationship('Maintenance', backref=db.backref('expenses', lazy=True))
    
    def __repr__(self):
        return f"<Expense {self.category} - Amount: {self.amount} on {self.date}>"
