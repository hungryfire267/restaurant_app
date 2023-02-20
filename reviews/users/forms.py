from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_login import current_user
from reviews import app

images = UploadSet('images', IMAGES)
configure_uploads(app, images)



def username_check(form, field): 
    if (len(field.data) < 6) or (len(field.data) > 20):
        raise ValidationError("Length of username must be between 6 characters and 20 characters long")

def password_check_length(form, field): 
    if (len(field.data) < 6 or len(field.data) > 20): 
        raise ValidationError("Length of the password must be between 6 characters and 20 characters long. ")

def password_check_capital(form, field):    
    if not any(element.isupper() for element in field.data): 
        raise ValidationError("There must be a capital letter. ")

def password_check_lowercase(form, field):
    if not any(element.islower() for element in field.data): 
        raise ValidationError("There must be a lowercase letter. ")

def username_verification(form, field): 
    if (current_user.username != form.username.data): 
        raise ValidationError("Username doesn't match with your current username.")

def password_verification(form, field): 
    if (current_user.password != form.old_password.data): 
        raise ValidationError("Inputted password doesn't match with your current password")

class registration_form(FlaskForm): 
    username = StringField('Username', validators=[DataRequired(), username_check])
    email = StringField('Email', validators=[DataRequired(), Email()])
    location = SelectField('Which City are you in right now?',
        choices = [('Sydney', 'Sydney'), ('Melbourne', 'Melbourne'), ('Brisbane', 'Brisbane'), 
            ('Perth', 'Perth'), ('Adelaide', 'Adelaide'), ('Hobart', 'Hobart'), ('Canberra', 'Canberra')])
    password = PasswordField('Password', validators=[DataRequired(), password_check_length, password_check_capital, password_check_lowercase])
    confirmed_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class login_form(FlaskForm): 
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')
    
class edit_username_form(FlaskForm): 
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Submit')

class edit_password_form(FlaskForm): 
    username = StringField('Username', validators=[DataRequired(), username_verification])
    old_password = StringField('Enter current password', validators=[DataRequired(), password_verification])
    new_password = StringField('Enter new password', validators=[DataRequired(), 
        password_check_length, password_check_capital, password_check_lowercase])
    confirmed_new_password = StringField('Confirm new password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Submit')
    
class edit_profile_picture_form(FlaskForm):
    picture = FileField('image', validators=[FileRequired(), FileAllowed(images, 'Images Only!')])
    submit = SubmitField('Submit')

class edit_location_form(FlaskForm): 
    location = SelectField('Which City are you in right now?',
        choices = [('Sydney', 'Sydney'), ('Melbourne', 'Melbourne'), ('Brisbane', 'Brisbane'), 
            ('Perth', 'Perth'), ('Adelaide', 'Adelaide'), ('Hobart', 'Hobart'), ('Canberra', 'Canberra')])
    submit = SubmitField('Submit')
    
class my_posts_form(FlaskForm):
    search = StringField('Post ID to Search')
    submit = SubmitField('Search')