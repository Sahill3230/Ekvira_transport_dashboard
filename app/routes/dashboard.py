from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from sqlalchemy import func
from datetime import datetime, date, timedelta
from app.models import db
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.trip import Trip
from app.models.fuel import Fuel
from app.models.maintenance import Maintenance
from app.models.expense import Expense
from app.models.destination import Destination
from app.models.income import Income
from app.models.notification import Notification

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    today = date.today()
    start_of_month = date(today.year, today.month, 1)
    
    # 1. Vehicle Counts
    total_vehicles = Vehicle.query.count()
    running_vehicles = Vehicle.query.filter_by(status='Active').count()
    idle_vehicles = Vehicle.query.filter_by(status='Idle').count()
    maint_vehicles = Vehicle.query.filter_by(status='Maintenance').count()
    
    # 2. Trip Counts (Today's)
    today_trips_count = Trip.query.filter_by(start_date=today).count()
    completed_trips_count = Trip.query.filter_by(status='Delivered').count()
    active_trips_count = Trip.query.filter(Trip.status.in_(['Loading', 'Running'])).count()
    
    # 3. Revenue Metrics
    # Today's Revenue (Freight income recorded today)
    today_revenue_q = db.session.query(func.sum(Income.amount)).filter(Income.date == today).scalar()
    today_revenue = float(today_revenue_q or 0.0)
    
    # Monthly Revenue (Income in current calendar month)
    monthly_revenue_q = db.session.query(func.sum(Income.amount)).filter(Income.date >= start_of_month).scalar()
    monthly_revenue = float(monthly_revenue_q or 0.0)
    
    # Monthly Expenses (recorded in current calendar month)
    monthly_expenses_q = db.session.query(func.sum(Expense.amount)).filter(Expense.date >= start_of_month).scalar()
    monthly_expenses = float(monthly_expenses_q or 0.0)
    
    # Net Profit (Monthly)
    monthly_net_profit = monthly_revenue - monthly_expenses
    
    # Fuel Consumption (Monthly diesel filled in liters)
    monthly_fuel_q = db.session.query(func.sum(Fuel.fuel_filled)).filter(Fuel.date >= start_of_month).scalar()
    monthly_fuel = float(monthly_fuel_q or 0.0)
    
    # Total Coal Transported (All-time delivered tons)
    total_coal_q = db.session.query(func.sum(Trip.coal_weight)).filter(Trip.status == 'Delivered').scalar()
    total_coal = float(total_coal_q or 0.0)
    
    # All-time financials
    total_revenue_q = db.session.query(func.sum(Income.amount)).scalar()
    total_revenue = float(total_revenue_q or 0.0)
    total_expenses_q = db.session.query(func.sum(Expense.amount)).scalar()
    total_expenses = float(total_expenses_q or 0.0)
    total_profit = total_revenue - total_expenses
    
    # 4. Expiry / Alert Quick Metrics
    unread_alerts = Notification.query.filter_by(is_read=False).order_by(Notification.created_at.desc()).limit(5).all()
    
    # 5. Compile Data for Javascript Charts
    # Chart A: Daily Revenue (last 7 days)
    daily_rev_labels = []
    daily_rev_values = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        daily_rev_labels.append(day.strftime('%b %d'))
        rev = db.session.query(func.sum(Income.amount)).filter(Income.date == day).scalar() or 0.0
        daily_rev_values.append(float(rev))
        
    # Chart B: Expense Breakdown
    categories = ['Diesel', 'Driver Salary', 'Toll', 'Repair', 'Maintenance', 'Miscellaneous']
    expense_breakdown = {}
    for cat in categories:
        amt = db.session.query(func.sum(Expense.amount)).filter(Expense.category == cat).scalar() or 0.0
        expense_breakdown[cat] = float(amt)
        
    # Chart C: Trip Status Distribution
    trip_statuses = ['Loading', 'Running', 'Delivered', 'Cancelled']
    trip_status_data = {}
    for st in trip_statuses:
        trip_status_data[st] = Trip.query.filter_by(status=st).count()
        
    # Chart D: Destination Coal Delivery
    destinations = db.session.query(func.sum(Trip.coal_weight), Destination.name)\
        .join(Destination)\
        .filter(Trip.status == 'Delivered')\
        .group_by(Destination.name).all()
    dest_labels = [d[1] for d in destinations]
    dest_coal_wts = [float(d[0] or 0.0) for d in destinations]

    return render_template(
        'dashboard/index.html',
        total_vehicles=total_vehicles,
        running_vehicles=running_vehicles,
        idle_vehicles=idle_vehicles,
        maint_vehicles=maint_vehicles,
        today_trips_count=today_trips_count,
        completed_trips_count=completed_trips_count,
        active_trips_count=active_trips_count,
        today_revenue=today_revenue,
        monthly_revenue=monthly_revenue,
        monthly_expenses=monthly_expenses,
        monthly_net_profit=monthly_net_profit,
        monthly_fuel=monthly_fuel,
        total_coal=total_coal,
        total_revenue=total_revenue,
        total_expenses=total_expenses,
        total_profit=total_profit,
        unread_alerts=unread_alerts,
        
        # Charts variables passed as python lists
        daily_rev_labels=daily_rev_labels,
        daily_rev_values=daily_rev_values,
        expense_categories=categories,
        expense_values=[expense_breakdown[c] for c in categories],
        trip_status_labels=trip_statuses,
        trip_status_values=[trip_status_data[s] for s in trip_statuses],
        dest_labels=dest_labels,
        dest_coal_wts=dest_coal_wts
    )
