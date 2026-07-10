from datetime import datetime
from app.models import db

class Income(db.Model):
    __tablename__ = 'income'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False) # 'Freight Charges', 'Trip Income', 'Total Revenue'
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    description = db.Column(db.Text)
    
    # Optional relation identifiers
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to trip
    trip = db.relationship('Trip', backref=db.backref('incomes', lazy=True))
    
    def __repr__(self):
        return f"<Income {self.category} - Amount: {self.amount} on {self.date}>"
