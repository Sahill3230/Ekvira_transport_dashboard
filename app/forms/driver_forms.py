from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField, DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, NumberRange

class DriverForm(FlaskForm):
    name = StringField('Driver Name', validators=[DataRequired(), Length(max=100)])
    mobile = StringField('Mobile Number', validators=[DataRequired(), Length(min=10, max=15), Regexp(r'^\+?[0-9]{10,15}$', message="Enter a valid mobile number")])
    license_number = StringField('Driving License Number', validators=[DataRequired(), Length(max=50)])
    license_expiry = DateField('License Expiry Date', format='%Y-%m-%d', validators=[DataRequired()])
    address = TextAreaField('Residential Address', validators=[Length(max=500)])
    aadhaar_number = StringField('Aadhaar Card Number', validators=[DataRequired(), Length(12, 12), Regexp(r'^\d{12}$', message="Aadhaar must be exactly 12 digits")])
    joining_date = DateField('Joining Date', format='%Y-%m-%d', validators=[DataRequired()])
    salary = DecimalField('Monthly Salary (INR)', validators=[DataRequired(), NumberRange(min=0)])
    status = SelectField('Driver Status', choices=[('Active', 'Active'), ('Inactive', 'Inactive'), ('On Trip', 'On Trip')], validators=[DataRequired()])
    submit = SubmitField('Save Driver')
