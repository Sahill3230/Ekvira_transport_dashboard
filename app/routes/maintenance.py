from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import db
from app.models.maintenance import Maintenance
from app.models.vehicle import Vehicle
from app.models.expense import Expense
from app.forms.maintenance_forms import MaintenanceForm

maintenance_bp = Blueprint('maintenance', __name__, url_prefix='/maintenance')

@maintenance_bp.route('/')
@login_required
def index():
    logs = Maintenance.query.order_by(Maintenance.service_date.desc()).all()
    return render_template('maintenance/list.html', logs=logs)

@maintenance_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = MaintenanceForm()
    
    # Populate vehicle choices
    vehicles = Vehicle.query.all()
    form.vehicle_id.choices = [(v.id, f"{v.vehicle_number} ({v.vehicle_name})") for v in vehicles]
    
    if form.validate_on_submit():
        v = Vehicle.query.get(form.vehicle_id.data)
        if not v:
            flash("Selected vehicle is invalid.", "danger")
            return render_template('maintenance/form.html', form=form, title="Log Maintenance")
            
        maint = Maintenance(
            vehicle_id=v.id,
            service_date=form.service_date.data,
            next_service_date=form.next_service_date.data,
            tyre_change=form.tyre_change.data,
            oil_change=form.oil_change.data,
            battery_change=form.battery_change.data,
            service_cost=form.service_cost.data,
            workshop_name=form.workshop_name.data,
            details=form.details.data
        )
        db.session.add(maint)
        db.session.commit() # commit to generate ID
        
        # Determine category based on whether tyres changed (Repair vs Maintenance)
        category = "Repair" if form.tyre_change.data or form.battery_change.data else "Maintenance"
        
        exp = Expense(
            category=category,
            amount=form.service_cost.data,
            date=form.service_date.data,
            description=f"Logged maintenance service at {form.workshop_name}. Tyres: {form.tyre_change.data}, Oil: {form.oil_change.data}, Battery: {form.battery_change.data}.",
            vehicle_id=v.id,
            maintenance_id=maint.id
        )
        db.session.add(exp)
        db.session.commit()
        
        flash(f"Maintenance ticket logged for vehicle {v.vehicle_number} at {form.workshop_name}.", "success")
        return redirect(url_for('maintenance.index'))
        
    return render_template('maintenance/form.html', form=form, title="Log Maintenance")

@maintenance_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    maint = Maintenance.query.get_or_404(id)
    
    # Delete connected expenses in expense book
    expenses = Expense.query.filter_by(maintenance_id=maint.id).all()
    for exp in expenses:
        db.session.delete(exp)
        
    db.session.delete(maint)
    db.session.commit()
    flash("Maintenance record and related expense logs deleted successfully.", "success")
    return redirect(url_for('maintenance.index'))
