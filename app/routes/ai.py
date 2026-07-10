from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.models.vehicle import Vehicle
from app.models.destination import Destination
from app.services.ai_service import (
    predict_maintenance_due,
    predict_fuel_consumption,
    predict_trip_time,
    predict_next_month_profit,
    get_ai_recommendations
)

ai_bp = Blueprint('ai', __name__, url_prefix='/ai')

@ai_bp.route('/analytics')
@login_required
def analytics():
    vehicles = Vehicle.query.all()
    destinations = Destination.query.all()
    
    # 1. Fetch profit prediction for next month
    predicted_profit = predict_next_month_profit()
    
    # 2. Get active list of AI optimization recommendations
    recommendations = get_ai_recommendations()
    
    # 3. Compile stats on high-risk vehicles
    maint_predictions = []
    for v in vehicles:
        risk = predict_maintenance_due(v.id)
        maint_predictions.append({
            "vehicle_number": v.vehicle_number,
            "vehicle_name": v.vehicle_name,
            "risk_percentage": risk,
            "status": v.status
        })
    # Sort by risk percentage descending
    maint_predictions = sorted(maint_predictions, key=lambda x: x["risk_percentage"], reverse=True)
    
    return render_template(
        'ai/analytics.html',
        vehicles=vehicles,
        destinations=destinations,
        predicted_profit=predicted_profit,
        recommendations=recommendations,
        maint_predictions=maint_predictions
    )

@ai_bp.route('/predict/maintenance', methods=['POST'])
@login_required
def api_predict_maintenance():
    vehicle_id = request.form.get('vehicle_id', type=int)
    if not vehicle_id:
        return jsonify({"error": "Vehicle ID is required"}), 400
        
    prob = predict_maintenance_due(vehicle_id)
    return jsonify({
        "vehicle_id": vehicle_id,
        "risk_percentage": prob,
        "verdict": "High servicing probability. Immediate maintenance recommended." if prob > 70.0 else "Normal operating state. Low risk of breakdown."
    })

@ai_bp.route('/predict/fuel', methods=['POST'])
@login_required
def api_predict_fuel():
    vehicle_id = request.form.get('vehicle_id', type=int)
    kms = request.form.get('kms', type=float)
    
    if not vehicle_id or not kms:
        return jsonify({"error": "Vehicle ID and Target Kilometers are required"}), 400
        
    predicted_liters = predict_fuel_consumption(vehicle_id, kms)
    # Average fuel price
    cost = predicted_liters * 95.00
    
    return jsonify({
        "vehicle_id": vehicle_id,
        "kms": kms,
        "predicted_fuel_liters": predicted_liters,
        "estimated_fuel_cost": round(cost, 2)
    })

@ai_bp.route('/predict/trip-time', methods=['POST'])
@login_required
def api_predict_trip_time():
    destination_id = request.form.get('destination_id', type=int)
    coal_weight = request.form.get('coal_weight', type=float)
    vehicle_id = request.form.get('vehicle_id', type=int)
    
    if not destination_id or not coal_weight or not vehicle_id:
        return jsonify({"error": "All fields are required"}), 400
        
    dest = Destination.query.get(destination_id)
    veh = Vehicle.query.get(vehicle_id)
    
    if not dest or not veh:
        return jsonify({"error": "Invalid destination or vehicle selection"}), 400
        
    predicted_hours = predict_trip_time(dest.distance, coal_weight, veh.capacity)
    
    return jsonify({
        "destination": dest.name,
        "distance": float(dest.distance),
        "capacity": float(veh.capacity),
        "coal_weight": coal_weight,
        "predicted_hours": predicted_hours,
        "eta_message": f"Estimated duration is {predicted_hours} hours. Average transit speed will be {round(float(dest.distance)/predicted_hours, 1)} km/h."
    })
