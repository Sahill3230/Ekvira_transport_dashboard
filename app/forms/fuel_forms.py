from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange

class FuelForm(FlaskForm):
    vehicle_id = SelectField('Vehicle', coerce=int, validators=[DataRequired()])
    date = DateField('Fuel Refill Date', format='%Y-%m-%d', validators=[DataRequired()])
    fuel_filled = DecimalField('Fuel Filled (Liters)', validators=[DataRequired(), NumberRange(min=1)])
    price = DecimalField('Fuel Price per Liter (INR)', validators=[DataRequired(), NumberRange(min=50)])
    mileage = DecimalField('Fuel Efficiency (km/l)', validators=[Optional(), NumberRange(min=2.0)])
    fuel_station = StringField('Fuel Station / Vendor Name', validators=[DataRequired()])
    submit = SubmitField('Record Refueling')
