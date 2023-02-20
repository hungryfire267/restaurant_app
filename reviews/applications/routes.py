import os
from flask import url_for, redirect, render_template, Blueprint
from flask_login import current_user
from reviews import app, db
from reviews.models import User, RestaurantUser, RestaurantUserComments
from reviews.applications.forms import restaurant_user_form, user_approval_form, restaurant_application
from reviews.applications.helper import restaurant_verifier, restaurant_app_list
from datetime import datetime

applications = Blueprint('applications', __name__)

# Application to apply to become a restaurant
@applications.route('/restaurant_app', methods=['GET', 'POST'])
def restaurant_app():
    if (current_user.role == 'admin' or current_user.role == 'restaurant'): 
        return redirect(url_for('users.account_info'))
    form = restaurant_user_form()
    if form.validate_on_submit(): 
        restaurant_user = RestaurantUser(name=form.name.data, restaurant=form.restaurant.data,
            address=form.address.data, info=form.info.data, explanation=form.explanation.data,
            user=current_user)
        db.session.add(restaurant_user)
        db.session.commit()
        return redirect(url_for('privileges.notifications_admin'))
    return render_template('restaurant_app.html', form=form)

# Administrators response for user to become a restaurant
@applications.route('/resolution/user_approval/<int:restaurant_user_id>', methods=['GET', 'POST'])
def user_approval(restaurant_user_id):
    if (current_user.role == 'restaurant' or current_user.role == 'regular'):
        return redirect(url_for('main.home'))
    form = user_approval_form()
    restaurant_user = RestaurantUser.query.get(restaurant_user_id)
    reason = restaurant_user.explanation
    if (restaurant_user.status == 'Resolved'):
        return redirect(url_for('privileges.notifications_admin'))
    restaurant = restaurant_user.restaurant
    address = restaurant_user.address
    restaurant_id = restaurant_verifier(restaurant, address)
    valid_restaurant = "No"
    if (restaurant_id is not None): 
        valid_restaurant = "Yes"
    potential_owner = User.query.filter_by(restaurant_id=restaurant_id).first()
    potential_owner_result = "No"
    if (potential_owner is not None): 
        potential_owner_result = "Yes"
    user = User.query.get(restaurant_user.user_id)
    user_ownership_result = "No"
    if (user.restaurant_id is not None):
        user_ownership_result = "Yes"
    with app.app_context():
        if form.validate_on_submit(): 
            statement = None
            if (form.status.data == 'Approve'): 
                statement = "Your application has been approved! You are now a restaurant owner!"
                user = User.query.get_or_404(restaurant_user.user_id)
                user.role = "restaurant"
                user.restaurant_id = restaurant_id
                db.session.commit()
            elif (valid_restaurant == "No"): 
                statement = "Your application has been denied because the restaurant is not in our database. A restaurant must have at least a review before a owner is added!"
            elif (potential_owner_result == "Yes"): 
                statement = "Your application has been denied because there is a user that owns this restaurant!"
            elif (user_ownership_result == "Yes"): 
                statement = "Your application has been denied because you own another restaurant!"
            else: 
                statement = "Your application has been denied because it doesn't meet our requirements!"
            restaurant_user = RestaurantUser.query.get(restaurant_user_id)
            restaurant_user_comment = RestaurantUserComments(comment = statement, restaurantuser = restaurant_user, post_time = datetime.utcnow())
            db.session.add(restaurant_user_comment)
            restaurant_user.status = "Resolved"
            db.session.commit()
            return redirect(url_for('privileges.notifications_admin'))
    return render_template('restaurant_user_approval.html', form=form, valid_restaurant=valid_restaurant,
        potential_owner_result=potential_owner_result, user_ownership_result=user_ownership_result,
        reason=reason)
    
# List of applications to become a restaurant and response from admin
@applications.route('/applications/restaurant', methods=['GET', 'POST'])
def application_restaurant(): 
    if (current_user.role == 'admin'):
        return redirect(url_for('main.home'))
    app_list = restaurant_app_list(current_user.id, '')
    path = f"C:/Users/Gordon Li/Desktop/restaurant_reviews/reviews/static/user/{current_user.id}"
    user_pic = None
    if (os.path.exists(path)):
        user_pic = os.listdir(path)[0]
    form = restaurant_application()
    if form.validate_on_submit(): 
        if form.search.data != '': 
            string = f"and r.id=\'{form.search.data}\'"
        else: 
            string = ''
        app_list = restaurant_app_list(current_user.id, string)
    return render_template('app_restaurant.html', app_list = app_list, user_pic=user_pic, form=form)