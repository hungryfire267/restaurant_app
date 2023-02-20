from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf.file import FileField, FileAllowed, FileRequired
from reviews import app
images = UploadSet('images', IMAGES)
configure_uploads(app, images)


class post_reviews_form(FlaskForm): 
    title = StringField('Title', validators=[DataRequired()])
    restaurant = StringField('Restaurant (exact match)', validators=[DataRequired()])
    restaurant_address = StringField('Address', validators=[DataRequired()])
    restaurant_cuisine = SelectField('Cuisine',
        choices = [('Australian', 'Australian'), ('American', 'American'), ('Chinese', 'Chinese'), ('Greek', 'Greek'), ('Indian', 'Indian'), 
        ('Italian', 'Italian'), ('Japanese', 'Japanese'), ('Korean', 'Korean'), ('Lebanese', 'Lebanese') , ('Mexican', 'Mexican'),
        ('Thai', 'Thai'), ('Turkish', 'Turkish'), ('Vietnamese', 'Vietnamese')])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    restaurant_rating = SelectField('Restaurant (service) rating', 
        choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])
    dish = StringField('Dish', validators=[DataRequired()])
    dish_type = StringField('Type of The Dish', validators=[DataRequired()])
    dish_rating = SelectField('Dish rating', 
        choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])
    dish_cost = DecimalField('Cost of the Dish', validators=[DataRequired()])
    dish_size = SelectField('Dish Size', choices = [('Small', 'Small'), ('Medium', 'Medium'), ('Large', 'Large')])
    value = SelectField('Value for money', choices = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])
    content = TextAreaField('Content', validators=[DataRequired()], render_kw={"rows": 5})
    restaurant_image = FileField('restaurant_image', validators=[FileAllowed(images, 'Images Only!')])
    dish_image = FileField('dish_image', validators=[FileAllowed(images, 'Images Only!')])
    submit = SubmitField('Post')
    
class edit_post_form(FlaskForm): 
    title = StringField('Title')
    restaurant_rating = SelectField('Restaurant (service) rating (*)', 
        choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])
    dish_rating = SelectField('Dish rating (*)', 
        choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])
    dish_cost = DecimalField('Cost of the Dish (*)', validators=[DataRequired()])
    dish_size = SelectField('Dish Size (*)', choices = [('Small', 'Small'), ('Medium', 'Medium'), ('Large', 'Large')])
    value = SelectField('Value for money (*)', choices = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])
    content = TextAreaField('Content', render_kw={"rows": 5})
    submit = SubmitField("Submit")