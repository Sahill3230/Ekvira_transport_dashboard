from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.models import db
from app.models.notification import Notification
from app.services.gps_service import get_simulated_gps_coordinates

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/vehicles/positions')
@login_required
def vehicle_positions():
    """Serves simulated vehicle coordinates for Leaflet JS updates."""
    try:
        positions = get_simulated_gps_coordinates()
        return jsonify(positions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/notifications/read/<int:id>', methods=['POST'])
@login_required
def mark_read(id):
    """Marks a single alert as read."""
    notif = Notification.query.get_or_404(id)
    notif.is_read = True
    db.session.commit()
    return jsonify({"success": True, "message": f"Notification #{id} marked as read."})

@api_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_read():
    """Marks all active alerts as read."""
    try:
        Notification.query.filter_by(is_read=False).update({Notification.is_read: True})
        db.session.commit()
        return jsonify({"success": True, "message": "All notifications marked as read."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
