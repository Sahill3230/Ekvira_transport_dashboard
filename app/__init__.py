from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from app.models import db
from app.models.user import User
from app.models.notification import Notification

csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    
    # Ensure database tables exist (useful for SQLite/dev)
    # We will trigger db creation on app start or during --seed run.
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.vehicles import vehicles_bp
    from app.routes.drivers import drivers_bp
    from app.routes.destinations import destinations_bp
    from app.routes.trips import trips_bp
    from app.routes.fuel import fuel_bp
    from app.routes.maintenance import maintenance_bp
    from app.routes.ai import ai_bp
    from app.routes.reports import reports_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(vehicles_bp)
    app.register_blueprint(drivers_bp)
    app.register_blueprint(destinations_bp)
    app.register_blueprint(trips_bp)
    app.register_blueprint(fuel_bp)
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(api_bp)
    
    # Inject active notifications count globally into templates
    @app.context_processor
    def inject_global_data():
        try:
            unread_notifications = Notification.query.filter_by(is_read=False).order_by(Notification.created_at.desc()).all()
            return dict(
                unread_notifications=unread_notifications,
                unread_count=len(unread_notifications)
            )
        except Exception:
            return dict(unread_notifications=[], unread_count=0)
            
    # Add a custom helper filter for currency / numbers formatting
    @app.template_filter('format_currency')
    def format_currency(value):
        try:
            return f"₹{float(value):,.2f}"
        except (ValueError, TypeError):
            return value

    return app
