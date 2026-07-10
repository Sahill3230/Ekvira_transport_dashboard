from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateField, TimeField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length

class TripForm(FlaskForm):
    vehicle_id = SelectField('Vehicle', coerce=int, validators=[DataRequired()])
    driver_id = SelectField('Driver', coerce=int, validators=[DataRequired()])
    destination_id = SelectField('Destination (Power Plant/Factory)', coerce=int, validators=[DataRequired()])
    source = StringField('Source (Loading Point)', default='Plot (Vavoshi)', validators=[DataRequired(), Length(max=100)])
    coal_weight = DecimalField('Coal Loaded Weight (Tons)', validators=[DataRequired(), NumberRange(min=25.0, max=100.0)])
    
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    end_time = TimeField('End Time', validators=[Optional()])
    
    status = SelectField('Trip Status', choices=[
        ('Loading', 'Loading'),
        ('Running', 'Running'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled')
    ], validators=[DataRequired()])
    
    diesel_used = DecimalField('Diesel Consumption (Liters)', validators=[Optional(), NumberRange(min=0)])
    toll_cost = DecimalField('Toll Cost (INR)', validators=[Optional(), NumberRange(min=0)])
    misc_expense = DecimalField('Miscellaneous Expenses (INR)', validators=[Optional(), NumberRange(min=0)])
    
    submit = SubmitField('Save Trip')
