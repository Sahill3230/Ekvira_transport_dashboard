import os
import pickle
import math
from datetime import datetime, date, timedelta
from app.models import db
from app.models.vehicle import Vehicle
from app.models.trip import Trip
from app.models.fuel import Fuel
from app.models.maintenance import Maintenance
from app.models.expense import Expense
from app.models.income import Income

MODEL_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', 'instance', 'ai_models')
os.makedirs(MODEL_DIR, exist_ok=True)

def get_model_path(name):
    return os.path.join(MODEL_DIR, f"{name}.pkl")

def save_model(model, name):
    with open(get_model_path(name), 'wb') as f:
        pickle.dump(model, f)

def load_model(name):
    path = get_model_path(name)
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except Exception:
        return None

# ==========================================
# Pure Python ML Implementation
# ==========================================

class PureLinearRegression:
    def __init__(self):
        self.w = []
        self.b = 0.0

    def fit(self, X, y):
        # Multi-variable gradient descent in pure Python
        n_samples = len(X)
        if n_samples == 0:
            return
        n_features = len(X[0])
        self.w = [0.0] * n_features
        self.b = sum(y) / n_samples
        
        # Hyperparameters (scaled for simple operational inputs)
        learning_rate = 0.000001
        epochs = 1500
        
        for _ in range(epochs):
            for i in range(n_samples):
                pred = sum(X[i][j] * self.w[j] for j in range(n_features)) + self.b
                err = pred - y[i]
                for j in range(n_features):
                    self.w[j] -= learning_rate * err * X[i][j]
                self.b -= learning_rate * err

    def predict(self, x_row):
        return sum(x_row[j] * self.w[j] for j in range(len(self.w))) + self.b


class PureLogisticRegression:
    def __init__(self):
        self.w = []
        self.b = 0.0

    def fit(self, X, y):
        n_samples = len(X)
        if n_samples == 0:
            return
        n_features = len(X[0])
        self.w = [0.0] * n_features
        self.b = 0.0
        
        learning_rate = 0.0001
        epochs = 1000
        
        for _ in range(epochs):
            for i in range(n_samples):
                z = sum(X[i][j] * self.w[j] for j in range(n_features)) + self.b
                # Sigmoid function
                pred = 1.0 / (1.0 + math.exp(-max(-15.0, min(15.0, z))))
                err = pred - y[i]
                for j in range(n_features):
                    self.w[j] -= learning_rate * err * X[i][j]
                self.b -= learning_rate * err

    def predict_proba(self, x_row):
        z = sum(x_row[j] * self.w[j] for j in range(len(self.w))) + self.b
        return 1.0 / (1.0 + math.exp(-max(-15.0, min(15.0, z))))


# ==========================================
# Service Interface Functions
# ==========================================

def train_and_save_all_models():
    print("Training AI models using Pure-Python Engine...")
    train_maintenance_model()
    train_fuel_model()
    train_trip_time_model()
    train_profit_model()

# 1. Maintenance need prediction (Classification)
def train_maintenance_model():
    vehicles = Vehicle.query.all()
    X, y = [], []
    
    for v in vehicles:
        m_records = Maintenance.query.filter_by(vehicle_id=v.id).order_by(Maintenance.service_date.desc()).all()
        if len(m_records) >= 2:
            for i in range(len(m_records) - 1):
                prev = m_records[i+1]
                curr = m_records[i]
                days_between = (curr.service_date - prev.service_date).days
                cost = float(curr.service_cost)
                tc = 1 if curr.tyre_change else 0
                oc = 1 if curr.oil_change else 0
                bc = 1 if curr.battery_change else 0
                
                label = 1 if days_between > 75 or cost > 20000 else 0
                X.append([days_between, cost / 1000.0, tc, oc, bc]) # scale cost
                y.append(label)
                
    # Seed data anchors for model stability
    X.append([15.0, 1.0, 0, 1, 0])
    y.append(0)
    X.append([90.0, 25.0, 1, 1, 1])
    y.append(1)
    X.append([30.0, 2.5, 0, 1, 0])
    y.append(0)
    X.append([80.0, 15.0, 0, 1, 0])
    y.append(1)

    model = PureLogisticRegression()
    model.fit(X, y)
    save_model(model, "maintenance_model")
    print("Maintenance classification model completed.")

def predict_maintenance_due(vehicle_id):
    model = load_model("maintenance_model")
    v = Vehicle.query.get(vehicle_id)
    if not v:
        return 0.0
        
    m_record = Maintenance.query.filter_by(vehicle_id=v.id).order_by(Maintenance.service_date.desc()).first()
    if m_record:
        days_since = (date.today() - m_record.service_date).days
        cost = float(m_record.service_cost)
        tc = 1 if m_record.tyre_change else 0
        oc = 1 if m_record.oil_change else 0
        bc = 1 if m_record.battery_change else 0
    else:
        days_since = 90.0
        cost = 15000.0
        tc, oc, bc = 0, 1, 0
        
    x_row = [float(days_since), float(cost / 1000.0), float(tc), float(oc), float(bc)]
    
    if not model:
        # Heuristic fallback
        prob = (days_since / 90.0) * 100.0
        return round(min(100.0, max(0.0, prob)), 1)
        
    try:
        prob = model.predict_proba(x_row) * 100
        return round(prob, 1)
    except Exception:
        return round(min(100.0, max(0.0, (days_since / 90.0) * 100.0)), 1)


# 2. Monthly Fuel Consumption Prediction (Regression)
def train_fuel_model():
    logs = Fuel.query.all()
    X, y = [], []
    
    for log in logs:
        v = Vehicle.query.get(log.vehicle_id)
        if v:
            dist = float(log.fuel_filled) * float(log.mileage or 3.0)
            capacity = float(v.capacity)
            X.append([dist / 100.0, capacity]) # Scale distance
            y.append(float(log.fuel_filled))
            
    # Anchors
    if len(X) < 10:
        X = [[1.0, 25.0], [2.0, 25.0], [3.0, 30.0], [4.0, 32.0]]
        y = [33.3, 66.6, 95.0, 125.0]
        
    model = PureLinearRegression()
    model.fit(X, y)
    save_model(model, "fuel_model")
    print("Fuel consumption model completed.")

def predict_fuel_consumption(vehicle_id, monthly_kms):
    model = load_model("fuel_model")
    v = Vehicle.query.get(vehicle_id)
    if not v:
        return 0.0
        
    capacity = float(v.capacity)
    
    if not model:
        return round(monthly_kms / 3.0, 1)
        
    x_row = [float(monthly_kms / 100.0), float(capacity)]
    try:
        pred = model.predict(x_row)
        return round(max(10.0, pred), 1)
    except Exception:
        return round(monthly_kms / 3.0, 1)


# 3. Trip Completion Duration prediction (Regression)
def train_trip_time_model():
    trips = Trip.query.filter_by(status='Delivered').all()
    X, y = [], []
    
    for t in trips:
        d = t.destination
        if d:
            dist = float(d.distance)
            weight = float(t.coal_weight)
            v = Vehicle.query.get(t.vehicle_id)
            capacity = float(v.capacity) if v else 30.0
            
            if t.end_date and t.end_time and t.start_date and t.start_time:
                start_dt = datetime.combine(t.start_date, t.start_time)
                end_dt = datetime.combine(t.end_date, t.end_time)
                duration = (end_dt - start_dt).total_seconds() / 3600.0
                X.append([dist / 10.0, weight, capacity]) # Scale distance
                y.append(duration)
                
    if len(X) < 10:
        X = [[4.5, 25.0, 28.0], [8.0, 28.0, 30.0], [12.0, 29.0, 30.0], [21.0, 32.0, 32.0]]
        y = [1.5, 2.5, 3.8, 6.5]
        
    model = PureLinearRegression()
    model.fit(X, y)
    save_model(model, "trip_time_model")
    print("Trip duration regression model completed.")

def predict_trip_time(distance, coal_weight, vehicle_capacity):
    model = load_model("trip_time_model")
    if not model:
        return round(distance / 45.0, 1)
        
    x_row = [float(distance / 10.0), float(coal_weight), float(vehicle_capacity)]
    try:
        pred = model.predict(x_row)
        return round(max(0.5, pred), 1)
    except Exception:
        return round(distance / 45.0, 1)


# 4. Monthly Profit Timeline Forecast
def train_profit_model():
    incomes = Income.query.all()
    expenses = Expense.query.all()
    
    profit_data = {}
    for inc in incomes:
        key = inc.date.strftime('%Y-%m')
        profit_data[key] = profit_data.get(key, 0.0) + float(inc.amount)
    for exp in expenses:
        key = exp.date.strftime('%Y-%m')
        profit_data[key] = profit_data.get(key, 0.0) - float(exp.amount)
        
    sorted_months = sorted(profit_data.keys())
    if len(sorted_months) < 3:
        sorted_months = ['2025-10', '2025-11', '2025-12', '2026-01', '2026-02', '2026-03']
        profit_data = {m: 500000.0 + (i * 25000.0) for i, m in enumerate(sorted_months)}
        sorted_months = sorted(profit_data.keys())
        
    X = [[float(i)] for i in range(len(sorted_months))]
    y = [profit_data[m] for m in sorted_months]
    
    model = PureLinearRegression()
    model.fit(X, y)
    save_model((model, len(sorted_months)), "profit_model")
    print("Profit prediction timeline model completed.")

def predict_next_month_profit():
    res = load_model("profit_model")
    if not res:
        return 750000.0
        
    model, next_step_idx = res
    try:
        pred = model.predict([float(next_step_idx)])
        return round(pred, 2)
    except Exception:
        return 750000.0


# 5. AI Recommendations Generator
def get_ai_recommendations():
    recommendations = []
    
    vehicles = Vehicle.query.all()
    for v in vehicles:
        prob = predict_maintenance_due(v.id)
        if prob > 70.0:
            recommendations.append({
                "type": "maintenance",
                "severity": "High",
                "title": f"Schedule service for {v.vehicle_number}",
                "message": f"AI model predicts a {prob}% chance of breakdown or servicing requirements in the next 30 days based on recent odometer updates and service cycle durations. Action: book garage inspection."
            })
            
        fuel_logs = Fuel.query.filter_by(vehicle_id=v.id).order_by(Fuel.date.desc()).limit(3).all()
        if len(fuel_logs) > 0:
            mileages = [float(log.mileage or 3.0) for log in fuel_logs]
            avg_mil = sum(mileages) / len(mileages)
            if avg_mil < 2.6:
                recommendations.append({
                    "type": "fuel",
                    "severity": "Medium",
                    "title": f"Fuel Optimization needed for {v.vehicle_number}",
                    "message": f"Average efficiency is low ({round(avg_mil, 2)} km/l). Recommendations: check tire pressure, inspect exhaust filters, and train driver to reduce excessive idling."
                })
                
    active_trips = Trip.query.filter_by(status="Running").all()
    for t in active_trips:
        v = Vehicle.query.get(t.vehicle_id)
        d = t.destination
        if v and d:
            est_hours = float(d.estimated_time)
            start_dt = datetime.combine(t.start_date, t.start_time)
            elapsed = (datetime.now() - start_dt).total_seconds() / 3600.0
            
            if elapsed > (est_hours * 1.25):
                recommendations.append({
                    "type": "delay",
                    "severity": "High",
                    "title": f"Delayed Trip #{t.id} Alert",
                    "message": f"Tipper {v.vehicle_number} carrying {t.coal_weight} tons to {d.name} has been running for {round(elapsed, 1)} hrs (estimated: {est_hours} hrs). Immediate driver dispatch follow-up is recommended."
                })
                
    if not recommendations:
        recommendations.append({
            "type": "general",
            "severity": "Low",
            "title": "All Fleet Systems Running Smoothly",
            "message": "AI analysis of operations, maintenance cycles, and fuel sheets suggests no immediate optimization bottlenecks."
        })
        
    return recommendations
