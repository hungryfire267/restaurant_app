import os
from flask import url_for, redirect, render_template, Blueprint
from flask_login import current_user, login_required
from reviews import app, db
from reviews.models import Feedback, FeedbackComments
from reviews.feedbacks.forms import (
    feedback_form, resolve_feedback_bugs, resolve_feedback_suggestions, feedback_search
)
from reviews.feedbacks.helper import feedback_list

feedbacks = Blueprint('feedbacks', __name__)

# Asks for a user to input a optional feedback form
@feedbacks.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback(): 
    if (current_user.role == 'admin'):
        return redirect(url_for('main.home'))
    form = feedback_form()
    if form.validate_on_submit(): 
        with app.app_context(): 
            feedback = Feedback(title=form.title.data, category=form.category.data, content=form.content.data, user=current_user)
            db.session.add(feedback)
            db.session.commit()
        return redirect(url_for('main.home'))
    return render_template('feedback.html', form=form)

# Administrator resolves feedback (two kinds: suggestions and bugs)
@feedbacks.route('/resolution/feedback/<int:feedback_id>', methods=['GET', 'POST'])
@login_required
def feedback_resolution(feedback_id):
    if (current_user.role == 'restaurant' or current_user.role == 'regular'):
        return redirect(url_for('main.home'))
    with app.app_context(): 
        feedback = Feedback.query.get_or_404(feedback_id)
        if (feedback.solved == 'Resolved'):
            return redirect(url_for('privileges.notifications_admin'))
        if (feedback.category == 'bugs'): 
            form = resolve_feedback_bugs()
            if form.validate_on_submit(): 
                statement = None
                if (form.status.data == 'in_progress' and feedback.solved == 'seen(WIP)'):
                    return redirect(url_for('privileges.notifications_admin'))
                if (form.status.data == 'in_progress'): 
                    statement = "We have seen the bug we are working our hardest to fix it."
                    feedback.solved = 'seen(WIP)'
                else: 
                    statement = "We have solved the bug. Let us know if there are any more bugs!"
                    feedback.solved = 'Resolved'
                feedback_comments= FeedbackComments(comment=statement, feedback = feedback)
                db.session.add(feedback_comments)
                db.session.commit()
                return redirect(url_for('privileges.notifications_admin'))
            return render_template('feedback_resolve_bug.html', form=form)
        else: 
            form = resolve_feedback_suggestions()
            if form.validate_on_submit(): 
                if (form.status.data == 'Seen'): 
                    if (feedback.solved == 'seen(WIP)'):
                        return redirect(url_for('privileges.notifications_admin'))
                    feedback.solved = 'seen(WIP)'
                else: 
                    feedback.solved = 'Resolved'
                feedback_comments = FeedbackComments(comment = form.content.data, feedback=feedback)
                db.session.add(feedback_comments)
                db.session.commit()
                return redirect(url_for('privileges.notifications_admin'))
            return render_template('feedback_resolve_suggestion.html', form=form)

# User feedback comments and comments from the restaurant
@feedbacks.route('/applications/feedback', methods=['POST', 'GET'])
@login_required
def application_feedback(): 
    if (current_user.role == 'admin'):
        return redirect(url_for('main.home'))
    feedbacks = feedback_list(current_user.id, '')
    path = f"C:/Users/Gordon Li/Desktop/restaurant_reviews/reviews/static/user/{current_user.id}"
    user_pic = None
    if (os.path.exists(path)):
        user_pic = os.listdir(path)[0]
    form = feedback_search()
    if form.validate_on_submit(): 
        if form.search.data != '': 
            string = f"and f.id=\'{form.search.data}\'"
        else: 
            string = ''
        feedbacks = feedback_list(current_user.id, string)
            
    return render_template('app_feedback.html', feedbacks=feedbacks, user_pic=user_pic, form=form)
