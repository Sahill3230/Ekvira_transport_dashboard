// Fleet Live Tracking GPS Simulator Map using Leaflet.js

let map;
let markers = {};

// Helper to determine icon colors based on status
function getTruckIconHTML(status) {
    let color = '#fbbf24'; // Yellow for Idle
    if (status === 'Active') {
        color = '#10b981'; // Green for Running/Active
    } else if (status === 'Maintenance') {
        color = '#ef4444'; // Red for Servicing
    }
    
    return `
        <div style="
            background: ${color};
            width: 38px;
            height: 38px;
            border-radius: 50%;
            border: 3px solid #fff;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            font-size: 1.1rem;
            transition: all 0.3s;
        ">
            <i class="fas fa-truck"></i>
        </div>
    `;
}

function initMap() {
    // Center at loading point (Korba Coal Mine, Chhattisgarh)
    const startLat = 18.8267;
    const startLng = 73.1895;
    
    map = L.map('live-fleet-map').setView([startLat, startLng], 10);
    
    // Check if dark theme is active and set tile style
    const isDark = document.body.classList.contains('dark-theme');
    
    // OpenStreetMap standard tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18
    }).addTo(map);
    
    updateVehiclePositions();
    
    // Poll updates every 5 seconds
    setInterval(updateVehiclePositions, 5000);
}

function updateVehiclePositions() {
    fetch('/api/vehicles/positions')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error("GPS API Error:", data.error);
                return;
            }
            
            data.forEach(veh => {
                const lat = parseFloat(veh.latitude);
                const lng = parseFloat(veh.longitude);
                
                // Create custom divIcon styled by truck status
                const truckIcon = L.divIcon({
                    html: getTruckIconHTML(veh.status),
                    className: 'custom-leaflet-icon',
                    iconSize: [38, 38],
                    iconAnchor: [19, 19],
                    popupAnchor: [0, -20]
                });
                
                const popupContent = `
                    <div style="font-family: 'Outfit', sans-serif; min-width: 200px;">
                        <h6 style="margin: 0 0 8px; font-weight: 700; color: var(--text-primary);">
                            Tipper ${veh.vehicle_number}
                        </h6>
                        <table style="width: 100%; font-size: 0.85rem; border-collapse: collapse; color: var(--text-secondary);">
                            <tr><td style="padding: 2px 0;"><b>Driver:</b></td><td style="text-align:right;">${veh.driver}</td></tr>
                            <tr><td style="padding: 2px 0;"><b>Status:</b></td><td style="text-align:right;"><span class="status-badge ${veh.status === 'Active' ? 'status-active' : (veh.status === 'Maintenance' ? 'status-maintenance' : 'status-idle')}">${veh.status}</span></td></tr>
                            <tr><td style="padding: 2px 0;"><b>Trip Status:</b></td><td style="text-align:right;">${veh.trip_status}</td></tr>
                            <tr><td style="padding: 2px 0;"><b>Destination:</b></td><td style="text-align:right;">${veh.destination}</td></tr>
                            ${veh.trip_status === 'Running' ? `
                                <tr><td style="padding: 2px 0;"><b>Speed:</b></td><td style="text-align:right; color:#10b981; font-weight:bold;">${veh.speed} km/h</td></tr>
                                <tr><td style="padding: 2px 0;"><b>ETA:</b></td><td style="text-align:right; font-weight:bold; color:#3b82f6;">${veh.eta} hrs</td></tr>
                            ` : ''}
                        </table>
                    </div>
                `;
                
                if (markers[veh.vehicle_id]) {
                    // Update existing marker coordinate and content
                    markers[veh.vehicle_id].setLatLng([lat, lng]);
                    markers[veh.vehicle_id].setIcon(truckIcon);
                    markers[veh.vehicle_id].setPopupContent(popupContent);
                } else {
                    // Create new marker
                    const marker = L.marker([lat, lng], { icon: truckIcon })
                        .bindPopup(popupContent)
                        .addTo(map);
                        
                    markers[veh.vehicle_id] = marker;
                }
            });
        })
        .catch(err => console.error("Error fetching GPS feeds:", err));
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('live-fleet-map')) {
        initMap();
    }
});
