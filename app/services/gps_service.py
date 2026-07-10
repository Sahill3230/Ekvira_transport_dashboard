from datetime import datetime, date, time, timedelta
from app.models.vehicle import Vehicle
from app.models.trip import Trip
from app.models.destination import Destination

# Geographic Constants for Plot (Vavoshi) Loading yard, Raigad, Maharashtra
MINE_LAT = 18.8267
MINE_LNG = 73.1895

DESTINATION_COORDS = {
    "Taloja": (19.0667, 73.0833),
    "Roha": (18.4373, 73.1189),
    "Khopoli": (18.7842, 73.3422),
    "Karanje": (18.7300, 73.0100),
    "Rasayani": (18.8986, 73.1764),
    "Mahadhan": (18.7314, 72.8805),
    "Alana": (19.0100, 73.1200)
}

def get_simulated_gps_coordinates():
    """Generates real-time GPS locations and telemetries for all vehicles near Raigad/Navi Mumbai."""
    vehicles = Vehicle.query.all()
    results = []
    
    for v in vehicles:
        active_trip = Trip.query.filter_by(vehicle_id=v.id, status='Running').first()
        
        speed = 0.0
        eta_minutes = 0.0
        dest_name = "None"
        lat = float(v.current_latitude or MINE_LAT)
        lng = float(v.current_longitude or MINE_LNG)
        driver_name = v.driver.name if v.driver else "Unassigned"
        
        if active_trip:
            dest = active_trip.destination
            dest_name = dest.name
            dest_lat, dest_lng = DESTINATION_COORDS.get(dest.name, (MINE_LAT, MINE_LNG))
            
            start_dt = datetime.combine(active_trip.start_date, active_trip.start_time)
            elapsed_seconds = (datetime.now() - start_dt).total_seconds()
            est_seconds = float(dest.estimated_time) * 3600.0
            
            fraction = elapsed_seconds / est_seconds if est_seconds > 0 else 1.0
            fraction = min(1.0, max(0.0, fraction))
            
            # Linear interpolation along route
            lat = MINE_LAT + fraction * (dest_lat - MINE_LAT)
            lng = MINE_LNG + fraction * (dest_lng - MINE_LNG)
            
            v.current_latitude = lat
            v.current_longitude = lng
            
            if fraction < 1.0:
                speed = round(35.0 + (v.id % 3) * 8.0 + (elapsed_seconds % 5), 1) # simulated speeds (35-55 km/h for local ghat roads)
                remaining_sec = max(0.0, est_seconds - elapsed_seconds)
                eta_minutes = round(remaining_sec / 60.0, 1)
                v.status = "Active"
            else:
                speed = 0.0
                eta_minutes = 0.0
                v.status = "Active"
        else:
            if v.status == "Maintenance":
                # Simulated local workshop at Pen/Panvel highway
                lat, lng = 18.8350, 73.1650 
            else:
                v.status = "Idle"
                # Parked randomly inside Vavoshi Plot yard
                lat = MINE_LAT + (v.id % 5 - 2) * 0.0008
                lng = MINE_LNG + (v.id % 3 - 1) * 0.0008
                
            v.current_latitude = lat
            v.current_longitude = lng
            
        results.append({
            "vehicle_id": v.id,
            "vehicle_number": v.vehicle_number,
            "vehicle_name": v.vehicle_name,
            "driver": driver_name,
            "status": v.status,
            "trip_status": active_trip.status if active_trip else "Idle",
            "destination": dest_name,
            "latitude": lat,
            "longitude": lng,
            "speed": speed,
            "eta": round(eta_minutes / 60.0, 1) if active_trip else 0.0
        })
        
    return results
