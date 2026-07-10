from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models import db
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.forms.vehicle_forms import VehicleForm
from app.services.ai_service import predict_maintenance_due
from datetime import datetime

vehicles_bp = Blueprint('vehicles', __name__, url_prefix='/vehicles')

@vehicles_bp.route('/')
@login_required
def index():
    query_str = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    
    vehicles_query = Vehicle.query
    
    if query_str:
        vehicles_query = vehicles_query.filter(
            (Vehicle.vehicle_number.ilike(f'%{query_str}%')) | 
            (Vehicle.vehicle_name.ilike(f'%{query_str}%')) | 
            (Vehicle.model.ilike(f'%{query_str}%'))
        )
        
    if status_filter:
        vehicles_query = vehicles_query.filter(Vehicle.status == status_filter)
        
    vehicles = vehicles_query.all()
    
    # Pre-compute AI maintenance prediction for display on fleet index
    for v in vehicles:
        v.maintenance_risk = predict_maintenance_due(v.id)
        
    return render_template('vehicles/list.html', vehicles=vehicles, search=query_str, status_filter=status_filter)

@vehicles_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = VehicleForm()
    
    # Get available active drivers who do not have an assigned vehicle
    # Or drivers whose vehicle is not set yet
    available_drivers = Driver.query.filter(
        (Driver.status == 'Active') & 
        ((Driver.vehicle_id == None) | (Driver.vehicle_id == 0))
    ).all()
    
    choices = [(0, 'No Driver Assigned')] + [(d.id, f"{d.name} ({d.license_number})") for d in available_drivers]
    form.driver_id.choices = choices
    
    if form.validate_on_submit():
        drv_id = form.driver_id.data if form.driver_id.data > 0 else None
        
        # Check vehicle number uniqueness
        existing = Vehicle.query.filter_by(vehicle_number=form.vehicle_number.data).first()
        if existing:
            flash("Vehicle number already exists.", "danger")
            return render_template('vehicles/form.html', form=form, title="Add Vehicle")
            
        veh = Vehicle(
            vehicle_number=form.vehicle_number.data.upper(),
            vehicle_name=form.vehicle_name.data,
            model=form.model.data,
            registration_number=form.registration_number.data.upper(),
            capacity=form.capacity.data,
            insurance_date=form.insurance_date.data,
            fitness_date=form.fitness_date.data,
            puc_date=form.puc_date.data,
            status=form.status.data,
            odometer=form.odometer.data,
            fuel_type=form.fuel_type.data,
            driver_id=drv_id
        )
        db.session.add(veh)
        db.session.commit()
        
        # If a driver was assigned, update that driver's vehicle_id record
        if drv_id:
            drv = Driver.query.get(drv_id)
            if drv:
                drv.vehicle_id = veh.id
                db.session.commit()
                
        flash(f"Vehicle {veh.vehicle_number} added successfully.", "success")
        return redirect(url_for('vehicles.index'))
        
    return render_template('vehicles/form.html', form=form, title="Add Vehicle")

@vehicles_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    veh = Vehicle.query.get_or_404(id)
    form = VehicleForm(obj=veh)
    
    # Active drivers who don't have a vehicle OR are currently assigned to this vehicle
    available_drivers = Driver.query.filter(
        (Driver.status == 'Active') & 
        ((Driver.vehicle_id == None) | (Driver.vehicle_id == veh.id))
    ).all()
    
    choices = [(0, 'No Driver Assigned')] + [(d.id, f"{d.name} ({d.license_number})") for d in available_drivers]
    form.driver_id.choices = choices
    
    if request.method == 'GET':
        form.driver_id.data = veh.driver_id or 0
        
    if form.validate_on_submit():
        drv_id = form.driver_id.data if form.driver_id.data > 0 else None
        
        # Check uniqueness for modified number
        existing = Vehicle.query.filter(Vehicle.vehicle_number == form.vehicle_number.data, Vehicle.id != id).first()
        if existing:
            flash("Vehicle number already exists.", "danger")
            return render_template('vehicles/form.html', form=form, title="Edit Vehicle")
            
        # Clean previous driver relation if driver changed
        if veh.driver_id and veh.driver_id != drv_id:
            old_drv = Driver.query.get(veh.driver_id)
            if old_drv:
                old_drv.vehicle_id = None
                
        veh.vehicle_number = form.vehicle_number.data.upper()
        veh.vehicle_name = form.vehicle_name.data
        veh.model = form.model.data
        veh.registration_number = form.registration_number.data.upper()
        veh.capacity = form.capacity.data
        veh.insurance_date = form.insurance_date.data
        veh.fitness_date = form.fitness_date.data
        veh.puc_date = form.puc_date.data
        veh.status = form.status.data
        veh.odometer = form.odometer.data
        veh.fuel_type = form.fuel_type.data
        veh.driver_id = drv_id
        
        db.session.commit()
        
        # Sync the new driver mapping
        if drv_id:
            new_drv = Driver.query.get(drv_id)
            if new_drv:
                new_drv.vehicle_id = veh.id
                db.session.commit()
                
        flash(f"Vehicle {veh.vehicle_number} updated successfully.", "success")
        return redirect(url_for('vehicles.index'))
        
    return render_template('vehicles/form.html', form=form, title="Edit Vehicle", is_edit=True)

@vehicles_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    if current_user.role != 'Admin':
        flash("Unauthorized access. Admin role required to delete vehicles.", "danger")
        return redirect(url_for('vehicles.index'))
        
    veh = Vehicle.query.get_or_404(id)
    
    # Clean driver mappings before deleting
    driver = Driver.query.filter_by(vehicle_id=veh.id).first()
    if driver:
        driver.vehicle_id = None
        
    db.session.delete(veh)
    db.session.commit()
    flash("Vehicle deleted successfully.", "success")
    return redirect(url_for('vehicles.index'))

@vehicles_bp.route('/history/<int:id>')
@login_required
def history(id):
    veh = Vehicle.query.get_or_404(id)
    trips = veh.trips
    maintenance = veh.maintenance_records
    fuel = veh.fuel_records
    ai_risk = predict_maintenance_due(veh.id)
    
    return render_template(
        'vehicles/history.html', 
        vehicle=veh, 
        trips=trips, 
        maintenance=maintenance, 
        fuel=fuel,
        ai_risk=ai_risk
    )
