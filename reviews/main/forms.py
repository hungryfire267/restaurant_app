from flask_wtf import FlaskForm
from wtforms import SelectField, TimeField, StringField, SubmitField
from wtforms.validators import DataRequired

class finder_form(FlaskForm):
    date = SelectField('Date you want to eat (*)', choices=[])
    time = TimeField("Time you want to eat (*)", format='%H:%M', validators=[DataRequired()])
    location = StringField('Please enter location(s) you want to dine at')
    cuisine = SelectField('Cuisine (*)',
        choices = [('', 'Any'), ('Australian', 'Australian'), ('American', 'American'), ('Chinese', 'Chinese'), ('Greek', 'Greek'), ('Indian', 'Indian'), 
        ('Italian', 'Italian'), ('Japanese', 'Japanese'), ('Korean', 'Korean'), ('Lebanese', 'Lebanese') , ('Mexican', 'Mexican'),
        ('Thai', 'Thai'), ('Turkish', 'Turkish'), ('Vietnamese', 'Vietnamese')])
    dish_type = StringField('Dish Type', validators=[])
    submit = SubmitField('Submit')