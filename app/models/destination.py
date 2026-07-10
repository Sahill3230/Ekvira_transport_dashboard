from datetime import datetime
from app.models import db

class Destination(db.Model):
    __tablename__ = 'destinations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    distance = db.Column(db.Numeric(10, 2), nullable=False) # in km
    rate_per_ton = db.Column(db.Numeric(10, 2), nullable=False) # rate in Rs/ton or USD/ton
    estimated_time = db.Column(db.Numeric(5, 2), nullable=False) # in hours
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    trips = db.relationship('Trip', backref='destination', lazy=True)
    
    def __repr__(self):
        return f"<Destination {self.name} - Distance: {self.distance} km>"
