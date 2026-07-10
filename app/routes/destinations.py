from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models import db
from app.models.destination import Destination

destinations_bp = Blueprint('destinations', __name__, url_prefix='/destinations')

@destinations_bp.route('/')
@login_required
def index():
    destinations = Destination.query.all()
    return render_template('destinations/list.html', destinations=destinations)

@destinations_bp.route('/add', methods=['POST'])
@login_required
def add():
    name = request.form.get('name')
    distance = request.form.get('distance')
    rate_per_ton = request.form.get('rate_per_ton')
    estimated_time = request.form.get('estimated_time')
    
    if not name or not distance or not rate_per_ton or not estimated_time:
        flash("All fields are required to add a destination.", "danger")
        return redirect(url_for('destinations.index'))
        
    try:
        dist_val = float(distance)
        rate_val = float(rate_per_ton)
        est_val = float(estimated_time)
    except ValueError:
        flash("Numeric fields must contain valid decimal numbers.", "danger")
        return redirect(url_for('destinations.index'))
        
    existing = Destination.query.filter_by(name=name).first()
    if existing:
        flash(f"Destination '{name}' already exists.", "danger")
        return redirect(url_for('destinations.index'))
        
    dest = Destination(
        name=name,
        distance=dist_val,
        rate_per_ton=rate_val,
        estimated_time=est_val
    )
    db.session.add(dest)
    db.session.commit()
    flash(f"Destination {name} added successfully.", "success")
    return redirect(url_for('destinations.index'))

@destinations_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    dest = Destination.query.get_or_404(id)
    
    name = request.form.get('name')
    distance = request.form.get('distance')
    rate_per_ton = request.form.get('rate_per_ton')
    estimated_time = request.form.get('estimated_time')
    
    if not name or not distance or not rate_per_ton or not estimated_time:
        flash("All fields are required to update a destination.", "danger")
        return redirect(url_for('destinations.index'))
        
    try:
        dist_val = float(distance)
        rate_val = float(rate_per_ton)
        est_val = float(estimated_time)
    except ValueError:
        flash("Numeric fields must contain valid decimal numbers.", "danger")
        return redirect(url_for('destinations.index'))
        
    # Check uniqueness
    existing = Destination.query.filter(Destination.name == name, Destination.id != id).first()
    if existing:
        flash(f"Destination '{name}' already exists.", "danger")
        return redirect(url_for('destinations.index'))
        
    dest.name = name
    dest.distance = dist_val
    dest.rate_per_ton = rate_val
    dest.estimated_time = est_val
    
    db.session.commit()
    flash(f"Destination {name} updated successfully.", "success")
    return redirect(url_for('destinations.index'))

@destinations_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    if current_user.role != 'Admin':
        flash("Unauthorized access. Admin role required to delete destinations.", "danger")
        return redirect(url_for('destinations.index'))
        
    dest = Destination.query.get_or_404(id)
    
    # Check if destination is used in any trips
    if len(dest.trips) > 0:
        flash(f"Cannot delete destination '{dest.name}' because it has trip logs associated with it.", "warning")
        return redirect(url_for('destinations.index'))
        
    db.session.delete(dest)
    db.session.commit()
    flash("Destination deleted successfully.", "success")
    return redirect(url_for('destinations.index'))
