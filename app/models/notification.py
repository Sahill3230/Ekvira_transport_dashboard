from datetime import datetime
from app.models import db

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=True)
    type = db.Column(db.String(50), nullable=False) # 'Service Due', 'Insurance Expiry', 'Fitness Expiry', 'PUC Expiry', 'License Expiry', 'Low Fuel', 'Breakdown', 'Trip Delay'
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    vehicle = db.relationship('Vehicle', backref=db.backref('notifications', lazy=True))
    driver = db.relationship('Driver', backref=db.backref('notifications', lazy=True))
    
    def __repr__(self):
        return f"<Notification Type: {self.type} - Read: {self.is_read}>"
