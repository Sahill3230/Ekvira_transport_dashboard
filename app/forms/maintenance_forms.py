from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange

class MaintenanceForm(FlaskForm):
    vehicle_id = SelectField('Vehicle', coerce=int, validators=[DataRequired()])
    service_date = DateField('Service Date', format='%Y-%m-%d', validators=[DataRequired()])
    next_service_date = DateField('Next Scheduled Service Date', format='%Y-%m-%d', validators=[DataRequired()])
    
    tyre_change = BooleanField('Tire Replaced')
    oil_change = BooleanField('Engine Oil Replaced')
    battery_change = BooleanField('Battery Replaced')
    
    service_cost = DecimalField('Total Service Cost (INR)', validators=[DataRequired(), NumberRange(min=0)])
    workshop_name = StringField('Workshop / Service Center Name', validators=[DataRequired()])
    details = TextAreaField('Additional Details / Comments', validators=[Optional()])
    
    submit = SubmitField('Log Maintenance')
