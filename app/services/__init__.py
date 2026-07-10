from app.services.ai_service import (
    train_and_save_all_models,
    predict_maintenance_due,
    predict_fuel_consumption,
    predict_trip_time,
    predict_next_month_profit,
    get_ai_recommendations
)
from app.services.gps_service import get_simulated_gps_coordinates
from app.services.notification_service import check_and_generate_notifications
