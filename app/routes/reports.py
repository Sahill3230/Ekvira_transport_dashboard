from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for
from flask_login import login_required
from io import BytesIO
import openpyxl
from datetime import datetime, date, timedelta
from app.models import db
from app.models.trip import Trip
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.fuel import Fuel
from app.models.expense import Expense
from app.models.income import Income

# ReportLab imports
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
def index():
    vehicles = Vehicle.query.all()
    drivers = Driver.query.all()
    return render_template('reports/index.html', vehicles=vehicles, drivers=drivers)

def get_report_data(report_type, start_date_str, end_date_str, vehicle_id=None, driver_id=None):
    """Aggregates matching dataset from database based on filters."""
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else date.today() - timedelta(days=30)
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else date.today()
    except ValueError:
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        
    title = f"{report_type.replace('_', ' ').title()} Report ({start_date} to {end_date})"
    headers = []
    rows = []
    
    if report_type in ['daily', 'weekly', 'monthly']:
        trips = Trip.query.filter(Trip.start_date.between(start_date, end_date)).order_by(Trip.start_date.desc()).all()
        headers = ['Trip ID', 'Date', 'Vehicle', 'Driver', 'Destination', 'Coal Weight (T)', 'Freight Amount (Rs)', 'Expenses (Rs)', 'Net Profit (Rs)', 'Status']
        
        for t in trips:
            v_num = t.vehicle.vehicle_number if t.vehicle else 'N/A'
            d_name = t.driver.name if t.driver else 'N/A'
            dest_name = t.destination.name if t.destination else 'N/A'
            
            diesel_cost = float(t.diesel_used or 0.0) * 95.00
            exp_val = diesel_cost + float(t.toll_cost or 0.0) + float(t.misc_expense or 0.0)
            
            rows.append([
                t.id, t.start_date.strftime('%Y-%m-%d'), v_num, d_name, dest_name,
                float(t.coal_weight), float(t.freight_amount), round(exp_val, 2),
                float(t.profit or 0.0), t.status
            ])
            
    elif report_type == 'vehicle':
        v = Vehicle.query.get(vehicle_id) if vehicle_id else None
        if v:
            title = f"Vehicle Report: {v.vehicle_number} ({v.vehicle_name})"
            trips = Trip.query.filter(Trip.vehicle_id == v.id, Trip.start_date.between(start_date, end_date)).all()
            headers = ['Trip ID', 'Date', 'Destination', 'Weight (T)', 'Revenue (Rs)', 'Diesel Used (L)', 'Profit (Rs)', 'Status']
            for t in trips:
                dest_name = t.destination.name if t.destination else 'N/A'
                rows.append([
                    t.id, t.start_date.strftime('%Y-%m-%d'), dest_name, float(t.coal_weight),
                    float(t.freight_amount), float(t.diesel_used or 0.0), float(t.profit or 0.0), t.status
                ])
                
    elif report_type == 'driver':
        d = Driver.query.get(driver_id) if driver_id else None
        if d:
            title = f"Driver Performance Report: {d.name} ({d.license_number})"
            trips = Trip.query.filter(Trip.driver_id == d.id, Trip.start_date.between(start_date, end_date)).all()
            headers = ['Trip ID', 'Date', 'Vehicle', 'Destination', 'Weight (T)', 'Revenue (Rs)', 'Profit (Rs)', 'Status']
            for t in trips:
                v_num = t.vehicle.vehicle_number if t.vehicle else 'N/A'
                dest_name = t.destination.name if t.destination else 'N/A'
                rows.append([
                    t.id, t.start_date.strftime('%Y-%m-%d'), v_num, dest_name, float(t.coal_weight),
                    float(t.freight_amount), float(t.profit or 0.0), t.status
                ])
                
    elif report_type == 'fuel':
        title = f"Fuel Consumption & Expense Report ({start_date} to {end_date})"
        fuels = Fuel.query.filter(Fuel.date.between(start_date, end_date)).order_by(Fuel.date.desc()).all()
        headers = ['ID', 'Date', 'Vehicle Number', 'Fuel Station', 'Filled (Liters)', 'Rate (Rs/L)', 'Total Expense (Rs)', 'Mileage (km/l)']
        for f in fuels:
            v_num = f.vehicle.vehicle_number if f.vehicle else 'N/A'
            qty = float(f.fuel_filled)
            rate = float(f.price)
            rows.append([
                f.id, f.date.strftime('%Y-%m-%d'), v_num, f.fuel_station or 'N/A',
                qty, rate, round(qty * rate, 2), float(f.mileage or 0.0)
            ])
            
    elif report_type == 'profit_loss':
        title = f"Profit & Loss (Income vs Expense) Ledger ({start_date} to {end_date})"
        incomes = Income.query.filter(Income.date.between(start_date, end_date)).all()
        expenses = Expense.query.filter(Expense.date.between(start_date, end_date)).all()
        
        headers = ['Date', 'Category', 'Description', 'Income (Rs)', 'Expense (Rs)']
        for inc in incomes:
            rows.append([inc.date.strftime('%Y-%m-%d'), inc.category, inc.description or 'Freight Income', float(inc.amount), 0.0])
        for exp in expenses:
            rows.append([exp.date.strftime('%Y-%m-%d'), exp.category, exp.description or 'Operational Expense', 0.0, float(exp.amount)])
            
        rows = sorted(rows, key=lambda x: x[0], reverse=True)

    return title, headers, rows

@reports_bp.route('/export/excel')
@login_required
def export_excel():
    report_type = request.args.get('type', 'daily')
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    vehicle_id = request.args.get('vehicle_id', type=int)
    driver_id = request.args.get('driver_id', type=int)
    
    title, headers, rows = get_report_data(report_type, start_date_str, end_date_str, vehicle_id, driver_id)
    
    # Create workbook and sheet in memory using openpyxl directly
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Report Summary"
    
    # Title Row
    ws.append([title])
    ws.append([]) # space
    
    # Headers
    ws.append(headers)
    
    # Data Rows
    for r in rows:
        formatted_row = []
        for val in r:
            if isinstance(val, float):
                formatted_row.append(round(val, 2))
            else:
                formatted_row.append(val)
        ws.append(formatted_row)
        
    # Write to BytesIO stream
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    filename = f"{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename
    )

@reports_bp.route('/export/pdf')
@login_required
def export_pdf():
    report_type = request.args.get('type', 'daily')
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    vehicle_id = request.args.get('vehicle_id', type=int)
    driver_id = request.args.get('driver_id', type=int)
    
    title, headers, rows = get_report_data(report_type, start_date_str, end_date_str, vehicle_id, driver_id)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0f172a'),
        alignment=1,
        spaceAfter=15
    )
    
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 15))
    
    table_data = [headers]
    for r in rows:
        formatted_row = []
        for val in r:
            if isinstance(val, float):
                formatted_row.append(f"{val:,.2f}")
            else:
                formatted_row.append(str(val))
        table_data.append(formatted_row)
        
    col_width_factor = 540 / len(headers)
    t = Table(table_data, colWidths=[col_width_factor]*len(headers))
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f1f5f9')])
    ]))
    story.append(t)
    
    doc.build(story)
    buffer.seek(0)
    
    filename = f"{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename
    )
