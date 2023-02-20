from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

# Form in which user provides feedback
class feedback_form(FlaskForm): 
    title = StringField('Title', validators=[DataRequired()])
    category = SelectField('Category', choices = [('bugs', 'Bugs'), ('suggestions', 'Suggestions')])
    content = TextAreaField('Content', validators=[DataRequired()], render_kw={"rows": 10})
    submit = SubmitField('Submit')

# Form in which feedback is resolved by admin (category being bugs)
class resolve_feedback_bugs(FlaskForm): 
    status = SelectField('Status', choices = [('in_progress', 'In Progress'), ('Resolved', 'Resolved')])
    submit = SubmitField('Submit')

# Form in which feedback is resolved by admin (category being suggestions)
class resolve_feedback_suggestions(FlaskForm):
    status = SelectField('Status', choices = [('Seen', 'Seen'), ('Resolved', 'Resolved')])
    content = TextAreaField('Content', validators = [DataRequired()], render_kw={"rows": 10})
    submit = SubmitField('Submit')

# Feedback posts searchbar
class feedback_search(FlaskForm): 
    search = StringField("Feedback ID to search")
    submit = SubmitField('Submit')