from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models import db
from app.models.driver import Driver
from app.models.vehicle import Vehicle
from app.forms.driver_forms import DriverForm

drivers_bp = Blueprint('drivers', __name__, url_prefix='/drivers')

@drivers_bp.route('/')
@login_required
def index():
    query_str = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    
    drivers_query = Driver.query
    
    if query_str:
        drivers_query = drivers_query.filter(
            (Driver.name.ilike(f'%{query_str}%')) | 
            (Driver.mobile.ilike(f'%{query_str}%')) | 
            (Driver.license_number.ilike(f'%{query_str}%'))
        )
        
    if status_filter:
        drivers_query = drivers_query.filter(Driver.status == status_filter)
        
    drivers = drivers_query.all()
    from datetime import date
    return render_template('drivers/list.html', drivers=drivers, search=query_str, status_filter=status_filter, today=date.today())

@drivers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = DriverForm()
    if form.validate_on_submit():
        # Check Aadhaar / License uniqueness
        existing_lic = Driver.query.filter_by(license_number=form.license_number.data).first()
        existing_aadhaar = Driver.query.filter_by(aadhaar_number=form.aadhaar_number.data).first()
        
        if existing_lic or existing_aadhaar:
            flash("License number or Aadhaar card already exists in the system.", "danger")
            return render_template('drivers/form.html', form=form, title="Add Driver")
            
        drv = Driver(
            name=form.name.data,
            mobile=form.mobile.data,
            license_number=form.license_number.data.upper(),
            license_expiry=form.license_expiry.data,
            address=form.address.data,
            aadhaar_number=form.aadhaar_number.data,
            joining_date=form.joining_date.data,
            salary=form.salary.data,
            status=form.status.data
        )
        db.session.add(drv)
        db.session.commit()
        flash(f"Driver {drv.name} added successfully.", "success")
        return redirect(url_for('drivers.index'))
        
    return render_template('drivers/form.html', form=form, title="Add Driver")

@drivers_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    drv = Driver.query.get_or_404(id)
    form = DriverForm(obj=drv)
    
    if form.validate_on_submit():
        # Check uniqueness for modified items
        existing_lic = Driver.query.filter(Driver.license_number == form.license_number.data, Driver.id != id).first()
        existing_aadhaar = Driver.query.filter(Driver.aadhaar_number == form.aadhaar_number.data, Driver.id != id).first()
        
        if existing_lic or existing_aadhaar:
            flash("License number or Aadhaar card already exists in the system.", "danger")
            return render_template('drivers/form.html', form=form, title="Edit Driver")
            
        drv.name = form.name.data
        drv.mobile = form.mobile.data
        drv.license_number = form.license_number.data.upper()
        drv.license_expiry = form.license_expiry.data
        drv.address = form.address.data
        drv.aadhaar_number = form.aadhaar_number.data
        drv.joining_date = form.joining_date.data
        drv.salary = form.salary.data
        drv.status = form.status.data
        
        db.session.commit()
        flash(f"Driver {drv.name} profile updated successfully.", "success")
        return redirect(url_for('drivers.index'))
        
    return render_template('drivers/form.html', form=form, title="Edit Driver", is_edit=True)

@drivers_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    if current_user.role != 'Admin':
        flash("Unauthorized access. Admin role required to delete drivers.", "danger")
        return redirect(url_for('drivers.index'))
        
    drv = Driver.query.get_or_404(id)
    
    # Clean vehicle mapping if assigned
    veh = Vehicle.query.filter_by(driver_id=drv.id).first()
    if veh:
        veh.driver_id = None
        
    db.session.delete(drv)
    db.session.commit()
    flash("Driver deleted successfully.", "success")
    return redirect(url_for('drivers.index'))

@drivers_bp.route('/profile/<int:id>')
@login_required
def profile(id):
    drv = Driver.query.get_or_404(id)
    trips = drv.trips_list
    total_trips = len(trips)
    delivered_trips = [t for t in trips if t.status == 'Delivered']
    total_delivered = len(delivered_trips)
    
    total_coal = sum([float(t.coal_weight) for t in delivered_trips])
    total_earnings = sum([float(t.freight_amount) for t in delivered_trips])
    
    return render_template(
        'drivers/profile.html', 
        driver=drv, 
        trips=trips, 
        total_trips=total_trips,
        total_delivered=total_delivered,
        total_coal=round(total_coal, 1),
        total_earnings=round(total_earnings, 2)
    )
