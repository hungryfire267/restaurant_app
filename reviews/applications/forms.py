from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired

# Application to become a restaurant
class restaurant_user_form(FlaskForm):
    name = StringField("Enter your name as shown in your passport", validators=[DataRequired()])
    restaurant = StringField("Please enter the restaurant you want to apply", validators=[DataRequired()])
    address = StringField("Please enter the address of your restaurant")
    info = TextAreaField('Please outline your restaurant in 100 or less words', validators=[DataRequired()], render_kw={"rows": 5})
    explanation = TextAreaField('Why do you want to enter your restaurant with us',
        validators = [DataRequired()], render_kw={"rows": 5})
    submit = SubmitField('Submit')

# Approval from Admin for user to become a restaurant
class user_approval_form(FlaskForm): 
    status = SelectField("Status", choices = [('Approve', 'Approve'), ('Decline', 'Decline')])
    submit = SubmitField('Submit')
    
# Application ID searchbar
class restaurant_application(FlaskForm): 
    search = StringField("Application ID to search")
    submit = SubmitField('Submit')
