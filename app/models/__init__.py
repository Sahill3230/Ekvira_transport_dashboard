from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models to register them with SQLAlchemy
from app.models.user import User
from app.models.driver import Driver
from app.models.vehicle import Vehicle
from app.models.destination import Destination
from app.models.trip import Trip
from app.models.fuel import Fuel
from app.models.maintenance import Maintenance
from app.models.expense import Expense
from app.models.income import Income
from app.models.notification import Notification
