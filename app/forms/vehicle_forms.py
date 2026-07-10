from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class VehicleForm(FlaskForm):
    vehicle_number = StringField('Vehicle Number (e.g., MH-12-PQ-1234)', validators=[DataRequired(), Length(max=20)])
    vehicle_name = StringField('Vehicle Name/Brand (e.g., Tata Signa)', validators=[DataRequired(), Length(max=100)])
    model = StringField('Model/Year', validators=[DataRequired(), Length(max=100)])
    registration_number = StringField('Registration Certificate (RC) Number', validators=[DataRequired(), Length(max=50)])
    capacity = DecimalField('Capacity (Tons)', validators=[DataRequired(), NumberRange(min=1, max=100)])
    driver_id = SelectField('Assign Driver', coerce=int)
    insurance_date = DateField('Insurance Expiry Date', format='%Y-%m-%d', validators=[DataRequired()])
    fitness_date = DateField('Fitness Certificate Expiry Date', format='%Y-%m-%d', validators=[DataRequired()])
    puc_date = DateField('PUC Expiry Date', format='%Y-%m-%d', validators=[DataRequired()])
    status = SelectField('Vehicle Status', choices=[('Idle', 'Idle'), ('Active', 'Active'), ('Maintenance', 'Maintenance')], validators=[DataRequired()])
    odometer = DecimalField('Odometer Reading (km)', validators=[DataRequired(), NumberRange(min=0)])
    fuel_type = SelectField('Fuel Type', choices=[('Diesel', 'Diesel'), ('CNG', 'CNG'), ('Electric', 'Electric')], validators=[DataRequired()])
    submit = SubmitField('Save Vehicle')
