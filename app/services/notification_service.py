from datetime import date, timedelta
from app.models import db
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.notification import Notification

def check_and_generate_notifications():
    """Scans compliance dates and active statuses to generate real-time database alerts."""
    today = date.today()
    warning_period = timedelta(days=15)
    
    # 1. Check Vehicle Compliance Expirations
    vehicles = Vehicle.query.all()
    for v in vehicles:
        # Insurance
        if v.insurance_date:
            days_left = (v.insurance_date - today).days
            if days_left <= 15:
                msg = f"Insurance for Vehicle {v.vehicle_number} expires in {days_left} days (on {v.insurance_date})."
                _create_unique_notification(v.id, None, "Insurance Expiry", msg)
                
        # Fitness Certificate
        if v.fitness_date:
            days_left = (v.fitness_date - today).days
            if days_left <= 15:
                msg = f"Fitness Certificate for Vehicle {v.vehicle_number} expires in {days_left} days (on {v.fitness_date})."
                _create_unique_notification(v.id, None, "Fitness Expiry", msg)
                
        # PUC Expiry
        if v.puc_date:
            days_left = (v.puc_date - today).days
            if days_left <= 15:
                msg = f"PUC Certificate for Vehicle {v.vehicle_number} expires in {days_left} days (on {v.puc_date})."
                _create_unique_notification(v.id, None, "PUC Expiry", msg)
                
    # 2. Check Driver License Expirations
    drivers = Driver.query.all()
    for d in drivers:
        if d.license_expiry:
            days_left = (d.license_expiry - today).days
            if days_left <= 15:
                msg = f"Driving License for {d.name} ({d.license_number}) expires in {days_left} days (on {d.license_expiry})."
                _create_unique_notification(None, d.id, "License Expiry", msg)
                
    db.session.commit()

def _create_unique_notification(vehicle_id, driver_id, n_type, message):
    """Ensures we don't spam duplicate alerts; only inserts if no active unread alert exists."""
    existing = Notification.query.filter_by(
        vehicle_id=vehicle_id,
        driver_id=driver_id,
        type=n_type,
        is_read=False
    ).first()
    
    if not existing:
        notif = Notification(
            vehicle_id=vehicle_id,
            driver_id=driver_id,
            type=n_type,
            message=message
        )
        db.session.add(notif)
