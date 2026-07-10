from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import db
from app.models.fuel import Fuel
from app.models.vehicle import Vehicle
from app.models.expense import Expense
from app.forms.fuel_forms import FuelForm

fuel_bp = Blueprint('fuel', __name__, url_prefix='/fuel')

@fuel_bp.route('/')
@login_required
def index():
    fuel_records = Fuel.query.order_by(Fuel.date.desc()).all()
    
    # Calculate vehicle-wise summaries for analytics dashboard card/charts
    vehicles = Vehicle.query.all()
    summaries = []
    for v in vehicles:
        logs = Fuel.query.filter_by(vehicle_id=v.id).all()
        total_qty = sum([float(log.fuel_filled) for log in logs])
        total_cost = sum([float(log.fuel_filled) * float(log.price) for log in logs])
        avg_mileage = sum([float(log.mileage or 3.0) for log in logs]) / len(logs) if logs else 0.0
        summaries.append({
            "vehicle_number": v.vehicle_number,
            "total_qty": round(total_qty, 1),
            "total_cost": round(total_cost, 2),
            "avg_mileage": round(avg_mileage, 2)
        })
        
    return render_template('fuel/list.html', fuel_records=fuel_records, summaries=summaries)

@fuel_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = FuelForm()
    
    # Populate vehicle dropdown selection list
    vehicles = Vehicle.query.all()
    form.vehicle_id.choices = [(v.id, f"{v.vehicle_number} ({v.vehicle_name})") for v in vehicles]
    
    if form.validate_on_submit():
        v = Vehicle.query.get(form.vehicle_id.data)
        if not v:
            flash("Selected vehicle is invalid.", "danger")
            return render_template('fuel/form.html', form=form, title="Log Refueling")
            
        fuel_qty = float(form.fuel_filled)
        fuel_price = float(form.price)
        total_cost = fuel_qty * fuel_price
        
        fuel_log = Fuel(
            vehicle_id=v.id,
            date=form.date.data,
            fuel_filled=fuel_qty,
            price=fuel_price,
            mileage=form.mileage.data,
            fuel_station=form.fuel_station.data
        )
        db.session.add(fuel_log)
        db.session.commit() # commit to generate fuel ID
        
        # Log refueling in expense book
        exp = Expense(
            category="Diesel",
            amount=total_cost,
            date=form.date.data,
            description=f"Recorded {fuel_qty}L at Rs.{fuel_price}/L (Station: {form.fuel_station.data})",
            vehicle_id=v.id
        )
        db.session.add(exp)
        db.session.commit()
        
        flash(f"Refueling of {fuel_qty}L for vehicle {v.vehicle_number} logged successfully.", "success")
        return redirect(url_for('fuel.index'))
        
    return render_template('fuel/form.html', form=form, title="Log Refueling")

@fuel_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    log = Fuel.query.get_or_404(id)
    
    # Find matching Diesel expense and delete it too
    ref_desc = f"Recorded {log.fuel_filled}L"
    exp = Expense.query.filter(
        Expense.vehicle_id == log.vehicle_id,
        Expense.date == log.date,
        Expense.category == 'Diesel',
        Expense.description.like(f'%{ref_desc}%')
    ).first()
    
    if exp:
        db.session.delete(exp)
        
    db.session.delete(log)
    db.session.commit()
    flash("Refueling log removed and corresponding fuel expense deleted.", "success")
    return redirect(url_for('fuel.index'))
