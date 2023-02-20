import os
from flask import (render_template, url_for, flash, redirect, request, Blueprint)
from flask_login import login_user, logout_user, current_user
from reviews import db, app
from reviews.models import User, Post
from reviews.users.forms import (registration_form, login_form, edit_username_form,
    edit_password_form, edit_profile_picture_form, edit_location_form, my_posts_form)
from reviews.users.helper import (directory_exists, transform_name, logo_remover,
                                  notifications_replies, notifications_feedback, notifications_approval
                                  ,image_adder, get_user_posts, user_dashboard_info)

users = Blueprint('users', __name__)

@users.route("/register", methods = ['GET', 'POST'])
def register(): 
    form = registration_form()
    if form.validate_on_submit():
        with app.app_context(): 
            user = User(username=form.username.data, email=form.email.data, location=form.location.data, 
                password=form.password.data)
            db.session.add(user)
            db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', form=form)

@users.route('/login', methods=['GET', 'POST'])
def login(): 
    if current_user.is_authenticated: 
        return redirect(url_for('users.account_info'))
    form = login_form()
    if form.validate_on_submit():
        with app.app_context():
            user = User.query.filter_by(email=form.email.data).first()
            if (user and user.password == form.password.data): 
                print(user.id)
                if(user.id == 1 and user.role == 'regular'):
                    user.role = 'admin'
                    db.session.commit()
                login_user(user)
                next = request.args.get('next')
                return redirect(next or url_for('users.account_info'))
            else: 
                flash('Cannot Login. Please change your email or password and try again!', 'danger')
    return render_template('login.html', form=form)

# Log User Out
@users.route('/logout')
def logout(): 
    logout_user()
    return redirect(url_for('main.home'))

# Gets Account Info
@users.route('/account_info')
def account_info(): 
    path = f"C:/Users/Gordon Li/Desktop/restaurant_reviews/reviews/static/user/{current_user.id}"
    profile_picture = 'default_user_profile.jpg'
    if (os.path.exists(path)):
        profile_picture = os.listdir(path)[0]
    return render_template('account_info.html', profile_picture=profile_picture)

# Edits account username
@users.route('/edit_username', methods=['GET', 'POST'])
def edit_username(): 
    form = edit_username_form()
    if form.validate_on_submit(): 
        with app.app_context():
            current_user.username = form.username.data
            db.session.commit()
        return redirect(url_for('users.account_info'))
    elif (request.method == 'GET'): 
        form.username.data = current_user.username
    return render_template('edit_username.html', form=form)

# Edits password
@users.route('/edit_password', methods=['GET', 'POST'])
def edit_password(): 
    form = edit_password_form()
    if form.validate_on_submit(): 
        with app.app_context(): 
            current_user.password = form.new_password.data
            db.session.commit() 
        return redirect(url_for('users.account_info'))
    return render_template('edit_password.html', form=form)

# Edits user profile picture
@users.route('/edit_profile_picture', methods=['GET', 'POST'])
def edit_profile_picture(): 
    path = f"C:/Users/Gordon Li/Desktop/restaurant_reviews/reviews/static/user/{current_user.id}"
    profile_picture = None
    if (os.path.exists(path)):
        profile_picture = os.listdir(path)[0]
    form = edit_profile_picture_form()
    if form.validate_on_submit(): 
        path = directory_exists('user', current_user.id)
        file = form.picture.data
        print(file.filename)
        new_filename = transform_name("user_pic", file.filename)
        print(new_filename)
        logo_remover("user_pic.", path)
        file.save(os.path.join(path, new_filename))
        return redirect(url_for('users.account_info'))
    return render_template('edit_profile_pic.html', form=form, profile_picture=profile_picture)

# Edits location user
@users.route('/edit_location', methods=['GET', 'POST'])
def edit_location(): 
    form = edit_location_form()
    if form.validate_on_submit(): 
        with app.app_context(): 
            current_user.location = form.location.data
            db.session.commit() 
        return redirect(url_for('users.account_info'))
    return render_template('edit_location.html', form=form)

# Gets notifications
@users.route('/notifications')
def notifications_regular(): 
    if (current_user.role == 'admin'): 
        return redirect(url_for('notifications_admin'))
    user_id = current_user.id
    notifications_reply = notifications_replies(user_id)
    notifications_feedbacks = notifications_feedback(user_id)
    approvals = notifications_approval(user_id)
    return render_template('notifications_regular.html', replies=notifications_reply, 
                           feedbacks=notifications_feedbacks, approvals=approvals)

# Gets account posts
@users.route('/account_posts', methods=['GET', 'POST'])
def account_posts(): 
    form = my_posts_form()
    new_list = get_user_posts(current_user.id, '')
    post_list = image_adder(new_list, 'account', current_user.id)
    user_id = current_user.id
    if form.validate_on_submit(): 
        if form.search.data != '':
            string = f"and p.id=\'{form.search.data}\'"
        else:
            string = ''
        new_list = get_user_posts(current_user.id, string)
        post_list = image_adder(new_list, 'account', current_user.id)
    print(post_list)
    return render_template('account_posts.html', form=form, post_list=post_list, owner=True, user_id=user_id)

# Get account dashboard
@users.route('/account_dashboard')
def account_dashboard(): 
    username = current_user.username
    user_id = current_user.id
    with app.app_context(): 
        posts = Post.query.filter_by(user_id=user_id).all()
        if (len(posts) == 0): 
            flash("Dashboard doesn't exist as user hasn't made a post yet", 'danger')
            return redirect(url_for('privileges.user_profile', user_id=user_id))
    count_wk, count_month, count_half_yr, count_yr, avg_restaurant, avg_dish,\
        cuisine_labels, cuisine_values, cost_labels, cost_values,\
        restaurant_labels, restaurant_values, dish_labels, dish_values,\
        popular_labels, popular_values, top_3_dish_labels, top_3_dish_values = user_dashboard_info(user_id)
    colours = ['#F9F9F9', '#E072A4', '#6883BA', '#3D3B8E', '#B0E298']
    popular_colors = colours[:len(popular_values)]
    top_3_dish_colors = colours[:len(top_3_dish_values)]
    avg_rating = (avg_restaurant + avg_dish)/2
    print(popular_colors)
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
        top_3_dish_colors=top_3_dish_colors, color=colours)

