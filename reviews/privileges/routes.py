from flask import render_template, url_for, redirect, flash, Blueprint
from flask_login import current_user, login_required
from reviews import db, app
from reviews.models import User, Post, Feedback, RestaurantUser
from reviews.privileges.forms import my_posts_form
from reviews.privileges.helper import (
    get_user_profile, get_user_posts, image_adder, user_dashboard_info
)

privileges = Blueprint('privileges', __name__)

#Gets user profile
@privileges.route('/user')
@login_required
def user(): 
    profile_settings = get_user_profile()
    return render_template('user_db.html', profile_settings=profile_settings)


@privileges.route('/user/<int:user_id>')
def user_profile(user_id): 
    if (user_id == current_user.id):
        return redirect(url_for('users.account_info'))
    user = User.query.filter_by(id=user_id).first()
    return render_template('user.html', user=user)

# Get User Posts
@privileges.route('/user/<int:user_id>/reviews', methods=['GET', 'POST'])
def user_posts(user_id): 
    if (user_id == current_user.id): 
        return redirect(url_for('users.account_posts'))
    user = User.query.filter_by(id=user_id).first()
    form = my_posts_form()
    new_list = get_user_posts(user_id, '')
    post_list = image_adder(new_list, 'account', user_id)
    if form.validate_on_submit(): 
        if form.search.data != '':
            string = f"and p.id=\'{form.search.data}\'"
        else:
            string = ''
        new_list = get_user_posts(user_id, string)
        post_list = image_adder(new_list, 'account', user_id)
    return render_template('account_posts.html', form=form, post_list=post_list, owner=False, user=user, user_id=user_id)

# Gets User Dashboard
@privileges.route('/user/<int:user_id>/dashboard')
def user_dashboard(user_id): 
    user = User.query.get_or_404(user_id)
    if (current_user.id == user_id): 
        return redirect(url_for('users.account_dashboard'))
    with app.app_context(): 
        posts = Post.query.filter_by(user_id=user_id).all()
        if (len(posts) == 0): 
            flash("Dashboard doesn't exist as user hasn't made a post yet", 'danger')
            return redirect(url_for('privileges.user_profile', user_id=user_id))
    username = user.username
    count_wk, count_month, count_half_yr, count_yr, avg_restaurant, avg_dish,\
        cuisine_labels, cuisine_values, cost_labels, cost_values,\
        restaurant_labels, restaurant_values, dish_labels, dish_values,\
        popular_labels, popular_values, top_3_dish_labels, top_3_dish_values = user_dashboard_info(user_id)
    colours = ['#F9F9F9', '#E072A4', '#6883BA', '#3D3B8E', '#B0E298']
    popular_colors = colours[:len(popular_values)]
    top_3_dish_colors = colours[:len(top_3_dish_values)]
    avg_rating = (avg_restaurant + avg_dish)/2
    print(restaurant_labels, restaurant_values, dish_labels, dish_values)
    return render_template('account_dashboard.html', username=username,
        count_wk=count_wk, count_month=count_month, count_half_yr=count_half_yr, count_yr=count_yr,
        avg_rating=avg_rating, avg_restaurant=avg_restaurant, avg_dish=avg_dish,
        cuisine_labels=cuisine_labels, cuisine_values=cuisine_values,
        cost_labels=cost_labels, cost_values=cost_values, 
        restaurant_labels=restaurant_labels, restaurant_values=restaurant_values,
        dish_labels=dish_labels, dish_values=dish_values,
        popular_labels=popular_labels, popular_values=popular_values,
        popular_colors=popular_colors,
        top_3_dish_labels=top_3_dish_labels, top_3_dish_values=top_3_dish_values,
        top_3_dish_colors=top_3_dish_colors,
        color=colours)
    
@privileges.route('/notifications/admin', methods=['GET', 'POST'])
def notifications_admin():
    if (current_user.role == 'admin'):
        feedbacks = Feedback.query.all()
        restaurant_users = RestaurantUser.query.filter_by(status="Unsolved").all()
        return render_template('notifications_admin.html', feedbacks=feedbacks,
            restaurant_users=restaurant_users)
    else: 
        return redirect(url_for('main.home'))