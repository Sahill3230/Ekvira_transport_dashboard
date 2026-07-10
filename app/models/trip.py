from datetime import datetime
from app.models import db

class Trip(db.Model):
    __tablename__ = 'trips'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.id'), nullable=False)
    
    source = db.Column(db.String(100), nullable=False, default='Mine Loading Point')
    coal_weight = db.Column(db.Numeric(10, 2), nullable=False)  # in tons
    start_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Loading') # 'Loading', 'Running', 'Delivered', 'Cancelled'
    
    freight_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0.0)
    diesel_used = db.Column(db.Numeric(10, 2), default=0.0)
    toll_cost = db.Column(db.Numeric(10, 2), default=0.0)
    misc_expense = db.Column(db.Numeric(10, 2), default=0.0)
    profit = db.Column(db.Numeric(12, 2), default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    driver = db.relationship('Driver', backref=db.backref('trips_list', lazy=True))
    
    def calculate_freight(self, rate_per_ton):
        self.freight_amount = self.coal_weight * rate_per_ton
        return self.freight_amount
        
    def calculate_profit(self, fuel_price=95.00):
        # Expenses: Diesel cost + Toll + Misc
        diesel_cost = self.diesel_used * fuel_price
        total_expenses = diesel_cost + self.toll_cost + self.misc_expense
        self.profit = self.freight_amount - total_expenses
        return self.profit
        
    def __repr__(self):
        return f"<Trip {self.id} - Vehicle: {self.vehicle_id} - Status: {self.status}>"
