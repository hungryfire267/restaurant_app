from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField

# Dish Type Search Form
class dish_search_form(FlaskForm):
    dish = SelectField('Dish', choices = [])
    submit = SubmitField('Submit')

# Search dish posts by dish, restaurant , sorted by a particular order
class dish_form(FlaskForm):
    dish = StringField('Dish', validators=[])
    restaurant = StringField('Restaurant', validators=[])
    sort = SelectField('Sort Reviews by (*)', choices=[('', 'None'), ('p.cost', 'Cost'), ('dish_rating', 'Dish Rating'), ('value', 'Value for Money'), ('size', 'Dish Size')])
    order = SelectField('Order by (*)', choices=[])
    submit = SubmitField('Submit')