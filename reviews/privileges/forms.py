from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

class my_posts_form(FlaskForm):
    search = StringField('Post ID to Search')
    submit = SubmitField('Search')