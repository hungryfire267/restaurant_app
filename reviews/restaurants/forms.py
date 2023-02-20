
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TimeField, TextAreaField
from wtforms.validators import DataRequired
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf.file import FileField, FileAllowed, FileRequired
from reviews import db, app

images = UploadSet('images', IMAGES)
configure_uploads(app, images)

# Restaurant Search Form
class restaurants_search_form(FlaskForm): 
    name = StringField('Select Restaurant Name')
    submit = SubmitField('Submit')

# Post Restaurant Searcher
class restaurants_filter_form(FlaskForm):
    dish = StringField('Dish')
    order = SelectField('Sort Reviews by (*)',
        choices = [('', '-'), ('asc,', 'Increasing'), ('desc,', 'Decreasing')]
    )
    type = SelectField('Order by (*)', 
        choices = [('', 'None'), ('p.cost', 'Cost'), ('p.dish_rating', 'Dish Rating'), 
                   ('p.restaurant_rating', 'Restaurant Rating'), 
                   ('p.value', 'Value for Money'), ('p.size', 'Size')]
    )
    submit = SubmitField('Submit')

# Edit Restaurant Address
class restaurant_address_form(FlaskForm): 
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Edit Restaurant phone
class restaurant_phone_form(FlaskForm):
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Edit Restaurant hour
class restaurant_hour_form(FlaskForm): 
    monday_morning = SelectField('Session 1 Status', choices=[('Open', 'Open'), ('Closed', 'Closed')])
    monday_morning_open = TimeField('Session 1 Opening', format='%H:%M', validators=[DataRequired()])
    monday_morning_close = TimeField('Session 1 Closing', format='%H:%M', validators=[DataRequired()])
    monday_evening = SelectField('Session 2 Status', choices=[('Open', 'Open'), ('Closed', 'Closed')])
    monday_evening_open = TimeField('Session 2 Opening', format='%H:%M', validators=[DataRequired()])
    monday_evening_close = TimeField('Session 2 Closing', format='%H:%M', validators=[DataRequired()])
    tuesday_morning = SelectField('Session 1 Status', choices=[('Open', 'Open'), ('Closed', 'Closed')])
    tuesday_morning_open = TimeField('Session 1 Opening', format='%H:%M', validators=[DataRequired()])
    tuesday_morning_close = TimeField('Session 1 Closing', format='%H:%M', validators=[DataRequired()])
    tuesday_evening = SelectField('Session 2 Status', choices=[('Open', 'Open'), ('Closed', 'Closed')])
    tuesday_evening_open = TimeField('Session 2 Opening', format='%H:%M', validators=[DataRequired()])
    tuesday_evening_close = TimeField('Session 2 Closing', format='%H:%M', validators=[DataRequired()])
    wednesday_morning = SelectField('Session 1 Status', choices=[('Open', 'Open'), ('Closed', 'Closed')])
    wednesday_morning_open = TimeField('Session 1 Opening', format='%H:%M', validators=[DataRequired()])
    wednesday_morning_close = TimeField('Session 1 Closing', format='%H:%M', validators=[DataRequired()])
    wednesday_evening = SelectField('Session 2 Status', choices=[('Open', 'Open'), ('Closed', 'Closed')])
    wednesday_evening_open = TimeField('Session 2 Opening', format='%H:%M', validators=[DataRequired()])
    wednesday_evening_close = TimeField('Session 2 Closing', format='%H:%M', validators=[DataRequired()])
    thursday_morning = SelectField('Session 1 Status', choices=[('Open', 'Open'), ('Closed', 'Closed')])
    thursday_morning_open = TimeField('Session 1 Opening', format='%H:%M', validators=[DataRequired()])
    thursday_morning_close = TimeField('Session 1 Closing', format='%H:%M', validators=[DataRequired()])
    thursday_evening = SelectField('Session 2 Status', choices=[('Open', 'Open'), ('Closed', 'Closed')])
    thursday_evening_open = TimeField('Session 2 Opening', format='%H:%M', validators=[DataRequired()])
    thursday_evening_close = TimeField('Session 2 Closing', format='%H:%M', validators=[DataRequired()])
    friday_morning = SelectField('Session 1 Status', choices=[('Open', 'Open'), ('Closed', 'Closed')])
    friday_morning_open = TimeField('Session 1 Opening', format='%H:%M', validators=[DataRequired()])
    friday_morning_close = TimeField('Session 1 Closing', format='%H:%M', validators=[DataRequired()])
    friday_evening = SelectField('Session 2 Status', choices=[('Open', 'Open'), ('Closed', 'Closed')])
    friday_evening_open = TimeField('Session 2 Opening', format='%H:%M', validators=[DataRequired()])
    friday_evening_close = TimeField('Session 2 Closing', format='%H:%M', validators=[DataRequired()])
    saturday_morning = SelectField('Session 1 Status', choices=[('Open', 'Open'), ('Closed', 'Closed')])
    saturday_morning_open = TimeField('Session 1 Opening', format='%H:%M', validators=[DataRequired()])
    saturday_morning_close = TimeField('Session 1 Closing', format='%H:%M', validators=[DataRequired()])
    saturday_evening = SelectField('Session 2 Status', choices=[('Open', 'Open'), ('Closed', 'Closed')])
    saturday_evening_open = TimeField('Session 2 Opening', format='%H:%M', validators=[DataRequired()])
    saturday_evening_close = TimeField('Session 2 Closing', format='%H:%M', validators=[DataRequired()])
    sunday_morning = SelectField('Session 1 Status', choices=[('Open', 'Open'), ('Closed', 'Closed')])
    sunday_morning_open = TimeField('Session 1 Opening', format='%H:%M', validators=[DataRequired()])
    sunday_morning_close = TimeField('Session 1 Closing', format='%H:%M', validators=[DataRequired()])
    sunday_evening = SelectField('Session 2 Status', choices=[('Open', 'Open'), ('Closed', 'Closed')])
    sunday_evening_open = TimeField('Session 2 Opening', format='%H:%M', validators=[DataRequired()])
    sunday_evening_close = TimeField('Session 2 Closing', format='%H:%M', validators=[DataRequired()])
    submit = SubmitField("Submit")

# Edit Restaurant logo
class restaurant_logo_form(FlaskForm):
    logo = FileField('image', validators=[FileRequired(), FileAllowed(images, 'Images Only!')])
    submit = SubmitField('Submit')
    
# Edit Restaurant comments
class restaurant_comments_form(FlaskForm): 
    comment = TextAreaField('Comment', validators=[DataRequired()], render_kw={"rows": 12})
    submit = SubmitField("Submit")
