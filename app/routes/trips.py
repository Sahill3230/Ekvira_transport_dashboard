from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models import db
from app.models.trip import Trip
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.destination import Destination
from app.models.expense import Expense
from app.models.income import Income
from app.forms.trip_forms import TripForm
from datetime import datetime, date, time
from app.utils.helpers import parse_date, parse_time

trips_bp = Blueprint('trips', __name__, url_prefix='/trips')

@trips_bp.route('/')
@login_required
def index():
    vehicle_filter = request.args.get('vehicle', '')
    driver_filter = request.args.get('driver', '')
    status_filter = request.args.get('status', '')
    dest_filter = request.args.get('destination', '')
    
    trips_query = Trip.query.order_by(Trip.start_date.desc(), Trip.start_time.desc())
    
    if vehicle_filter:
        trips_query = trips_query.join(Vehicle).filter(Vehicle.vehicle_number.ilike(f'%{vehicle_filter}%'))
    if driver_filter:
        trips_query = trips_query.join(Driver).filter(Driver.name.ilike(f'%{driver_filter}%'))
    if status_filter:
        trips_query = trips_query.filter(Trip.status == status_filter)
    if dest_filter:
        trips_query = trips_query.join(Destination).filter(Destination.name.ilike(f'%{dest_filter}%'))
        
    trips = trips_query.all()
    return render_template('trips/list.html', trips=trips)

@trips_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = TripForm()
    
    # Populate vehicle choices (only show Idle vehicles or Active vehicles not on trip, plus active drivers)
    idle_vehicles = Vehicle.query.filter_by(status='Idle').all()
    form.vehicle_id.choices = [(v.id, f"{v.vehicle_number} ({v.vehicle_name})") for v in idle_vehicles]
    
    active_drivers = Driver.query.filter_by(status='Active').all()
    form.driver_id.choices = [(d.id, f"{d.name} ({d.mobile})") for d in active_drivers]
    
    destinations = Destination.query.all()
    form.destination_id.choices = [(d.id, f"{d.name} ({d.distance} km @ Rs.{d.rate_per_ton}/T)") for d in destinations]
    
    # Pre-set current date and time
    if request.method == 'GET':
        form.start_date.data = date.today()
        form.start_time.data = datetime.now().time()
        
    if form.validate_on_submit():
        veh = Vehicle.query.get(form.vehicle_id.data)
        drv = Driver.query.get(form.driver_id.data)
        dest = Destination.query.get(form.destination_id.data)
        
        # Validation checks
        if not veh or not drv or not dest:
            flash("Selected vehicle, driver, or destination is invalid.", "danger")
            return render_template('trips/form.html', form=form, title="Create Trip")
            
        # Create trip object
        trip = Trip(
            vehicle_id=veh.id,
            driver_id=drv.id,
            destination_id=dest.id,
            source=form.source.data,
            coal_weight=form.coal_weight.data,
            start_date=form.start_date.data,
            start_time=form.start_time.data,
            status=form.status.data,
            freight_amount=form.coal_weight.data * dest.rate_per_ton
        )
        
        # Change statuses of vehicle and driver
        if trip.status in ['Loading', 'Running']:
            veh.status = 'Active'
            drv.status = 'On Trip'
            
        db.session.add(trip)
        db.session.commit()
        
        flash(f"Trip #{trip.id} created successfully.", "success")
        return redirect(url_for('trips.index'))
        
    return render_template('trips/form.html', form=form, title="Create Trip")

@trips_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    trip = Trip.query.get_or_404(id)
    form = TripForm(obj=trip)
    
    # Allow selection from all vehicles and drivers (to allow correction)
    vehicles = Vehicle.query.all()
    form.vehicle_id.choices = [(v.id, f"{v.vehicle_number} ({v.vehicle_name})") for v in vehicles]
    
    drivers = Driver.query.all()
    form.driver_id.choices = [(d.id, f"{d.name} ({d.mobile})") for d in drivers]
    
    destinations = Destination.query.all()
    form.destination_id.choices = [(d.id, f"{d.name} ({d.distance} km)") for d in destinations]
    
    if request.method == 'GET':
        form.vehicle_id.data = trip.vehicle_id
        form.driver_id.data = trip.driver_id
        form.destination_id.data = trip.destination_id
        
    if form.validate_on_submit():
        previous_status = trip.status
        new_status = form.status.data
        
        veh = Vehicle.query.get(form.vehicle_id.data)
        drv = Driver.query.get(form.driver_id.data)
        dest = Destination.query.get(form.destination_id.data)
        
        # Update properties
        trip.vehicle_id = veh.id
        trip.driver_id = drv.id
        trip.destination_id = dest.id
        trip.source = form.source.data
        trip.coal_weight = form.coal_weight.data
        trip.start_date = form.start_date.data
        trip.start_time = form.start_time.data
        trip.status = new_status
        trip.freight_amount = form.coal_weight.data * dest.rate_per_ton
        
        # Handle status transitions
        if new_status == 'Delivered':
            trip.end_date = form.end_date.data or date.today()
            trip.end_time = form.end_time.data or datetime.now().time()
            trip.diesel_used = form.diesel_used.data or 0.0
            trip.toll_cost = form.toll_cost.data or 0.0
            trip.misc_expense = form.misc_expense.data or 0.0
            
            # Calculate Profit
            diesel_price = 95.00 # average Diesel cost per liter
            trip.calculate_profit(fuel_price=diesel_price)
            
            # Clean and reset vehicle & driver status
            veh.status = 'Idle'
            drv.status = 'Active'
            
            # Update Odometer: adding round trip distance
            veh.odometer = float(veh.odometer) + (float(dest.distance) * 2)
            
            # Record Income (if not already logged)
            income_exist = Income.query.filter_by(trip_id=trip.id).first()
            if not income_exist:
                inc = Income(
                    category="Freight Charges",
                    amount=trip.freight_amount,
                    date=trip.end_date,
                    description=f"Revenue generated from Trip #{trip.id} to {dest.name}",
                    trip_id=trip.id
                )
                db.session.add(inc)
                
            # Record Expenses (if not already logged)
            diesel_exp_exist = Expense.query.filter_by(trip_id=trip.id, category='Diesel').first()
            if not diesel_exp_exist and float(trip.diesel_used) > 0:
                db.session.add(Expense(
                    category="Diesel",
                    amount=float(trip.diesel_used) * diesel_price,
                    date=trip.end_date,
                    description=f"Diesel cost for Trip #{trip.id}",
                    vehicle_id=veh.id,
                    trip_id=trip.id
                ))
            
            toll_exp_exist = Expense.query.filter_by(trip_id=trip.id, category='Toll').first()
            if not toll_exp_exist and float(trip.toll_cost) > 0:
                db.session.add(Expense(
                    category="Toll",
                    amount=trip.toll_cost,
                    date=trip.end_date,
                    description=f"Toll expenses for Trip #{trip.id}",
                    vehicle_id=veh.id,
                    trip_id=trip.id
                ))
                
            misc_exp_exist = Expense.query.filter_by(trip_id=trip.id, category='Miscellaneous').first()
            if not misc_exp_exist and float(trip.misc_expense) > 0:
                db.session.add(Expense(
                    category="Miscellaneous",
                    amount=trip.misc_expense,
                    date=trip.end_date,
                    description=f"Misc operational costs for Trip #{trip.id}",
                    vehicle_id=veh.id,
                    trip_id=trip.id
                ))
                
        elif new_status == 'Cancelled':
            veh.status = 'Idle'
            drv.status = 'Active'
            trip.profit = 0.0
            
        elif new_status in ['Loading', 'Running']:
            veh.status = 'Active'
            drv.status = 'On Trip'
            
        db.session.commit()
        flash(f"Trip #{trip.id} updated successfully.", "success")
        return redirect(url_for('trips.index'))
        
    return render_template('trips/form.html', form=form, title="Edit/Close Trip", is_edit=True, trip=trip)

@trips_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    if current_user.role != 'Admin':
        flash("Unauthorized access. Admin role required to delete trips.", "danger")
        return redirect(url_for('trips.index'))
        
    trip = Trip.query.get_or_404(id)
    
    # If the trip was running or active, reset vehicle/driver status
    if trip.status in ['Loading', 'Running']:
        veh = Vehicle.query.get(trip.vehicle_id)
        drv = Driver.query.get(trip.driver_id)
        if veh:
            veh.status = 'Idle'
        if drv:
            drv.status = 'Active'
            
    db.session.delete(trip)
    db.session.commit()
    flash("Trip log deleted.", "success")
    return redirect(url_for('trips.index'))
