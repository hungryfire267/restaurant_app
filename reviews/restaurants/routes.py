import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import (render_template, request, redirect, url_for, flash, Blueprint)
from flask_login import current_user, login_required
from reviews import db, app
from reviews.models import Restaurant, Post, Like, RestaurantHours, User, RestaurantComment
from reviews.restaurants.forms import (restaurants_search_form, restaurants_filter_form,
    restaurant_address_form, restaurant_phone_form, restaurant_hour_form, restaurant_logo_form,
    restaurant_comments_form)
from reviews.restaurants.helper import (get_restaurant_information, restaurant_info_simplifier,
                                get_averages, price_range, map_link_retriever, 
                                get_hours, get_restaurant_suburb, get_popular_restaurants_suburb,
                                dish_string, get_posts, image_adder,
                                get_restaurant_dish_images_sql, get_restaurant_dish_images, 
                                get_info,
                                logo_name_finder, get_city, valid_phone_number,
                                directory_exists, transform_name, logo_remover,
                                get_restaurant_rating_scores, get_dish_rating_scores,
                                convert_dict_ratings,
                                get_top_3, get_worst_3, get_popular_3, get_avg_cost,
                                get_posts_month_restaurant, get_posts_v2)

restaurants = Blueprint('restaurants', __name__)

# Search for a specific Restaurant
@restaurants.route('/restaurants', methods=['GET', 'POST'])
@login_required
def restaurant_search():
    if (current_user.role == 'restaurant'):
        return redirect(url_for('restaurants.restaurant', restaurant_id = current_user.restaurant_id)) 
    form = restaurants_search_form()
    restaurants_information = None
    print(restaurants_information)
    if form.validate_on_submit():
        restaurants_info = get_restaurant_information(form.name.data)
        print(restaurants_info)
        restaurants_information = restaurant_info_simplifier(restaurants_info)
        print(restaurants_information)
    return render_template('restaurant.html', form=form, restaurants=restaurants_information)

# Gets the profile of a restaurant
@restaurants.route('/restaurants/<int:restaurant_id>', methods=['GET', 'POST'])
@login_required
def restaurant(restaurant_id): 
    with app.app_context(): 
        if (current_user.role == 'restaurant' and current_user.restaurant_id != restaurant_id): 
            return redirect(url_for('restaurants.restaurant', restaurant_id = current_user.restaurant_id))
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        avg_restaurant_rating, avg_dish_rating, avg_dish_cost = get_averages(restaurant_id)
        avg_cost = price_range(avg_dish_cost)
        restaurant_type = restaurant.cuisine + ' restaurant'
        address = restaurant.address
        src = map_link_retriever(address)
        phone = restaurant.phone_number
        restaurant_ratings = get_restaurant_rating_scores(restaurant_id)
        no_reviews=len(restaurant_ratings)
        restaurant_ratings_keys, restaurant_ratings_values = convert_dict_ratings(restaurant_ratings)
        suburb, state = get_restaurant_suburb(address)
        restaurants_list = get_popular_restaurants_suburb(restaurant_id, suburb, state)
        form = restaurants_filter_form()
        new_list = []
        if form.validate_on_submit(): 
            dish_strings = dish_string(form.dish.data)
            if (form.type.data == '' and form.order.data != ''):
                statement = "You cannot select increasing or decreasing as an order by"
                flash(statement, 'danger')
            elif (form.type.data != '' and form.order.data == ''): 
                statement = "You must select increasing or decreasing as an order by"
                flash(statement, 'danger')
            else: 
                print(dish_strings)
                new_list = get_posts(restaurant_id, form.type.data, form.order.data, dish_strings)
                statement = "Success"
                flash(statement, 'success')
        else: 
            new_list= get_posts(restaurant_id, "", "", "")
        post_list = image_adder(new_list, 'restaurant', None)
        images_list = get_restaurant_dish_images_sql(restaurant_id)
        restaurant_images, dish_images = get_restaurant_dish_images(images_list)
        restaurant_images = sorted(restaurant_images, key=lambda x: str(x[3] is False))
        dish_images = sorted(dish_images, key=lambda x: str(x[3] is False))
        path = f"C:/Users/Gordon Li/Desktop/restaurant_reviews/reviews/static/restaurant/{restaurant_id}"
        logo_name = None
        if (os.path.exists(path)):
            logo_name = logo_name_finder(path)
        restaurant_id_str = str(restaurant_id)
        owner = User.query.filter_by(restaurant_id=restaurant_id).first()
        overview=None
        if owner: 
            overview=get_info(owner.id)
        hours = get_hours(restaurant_id)
        if request.form.get('like') == "1" or request.form.get('dislike') == "-1":
            post_id = request.form.get('post_id')
            valid_likes = Like.query.filter_by(user_id = current_user.id, post_id=post_id).first()
            if valid_likes == None and current_user.role == 'regular': 
                post = Post.query.filter_by(id=post_id).first() 
                upvotes = post.upvotes
                if request.form.get('like') == "1":
                    upvotes += 1
                elif request.form.get('dislike') == "-1": 
                    upvotes -= 1
                with app.app_context():
                    post = Post.query.filter_by(id=post_id).first() 
                    post.upvotes = upvotes
                    like_post = Like(user_id=current_user.id, post_id=post_id)
                    db.session.add(like_post)
                    db.session.commit()
            return redirect(url_for('restaurants.restaurant', restaurant_id=restaurant_id))
    return render_template(
        'restaurant_profile.html',  
        name = restaurant.name, cost=avg_cost, type = restaurant_type, address = address,
        phone = phone, avg_restaurant_rating = avg_restaurant_rating, 
        avg_dish_rating=avg_dish_rating, no_reviews=no_reviews, 
        src = src, restaurant_ratings_keys=restaurant_ratings_keys,
        restaurant_images=restaurant_images, dish_images=dish_images,
        restaurant_ratings_values=restaurant_ratings_values, form=form,
        post_list=post_list, suburb=suburb, restaurants_list=restaurants_list,
        restaurant_id= restaurant_id, restaurant=restaurant, overview=overview,
        hours=hours, logo_name=logo_name, restaurant_id_str=restaurant_id_str)

# Gets the restaurant settings if user is the restaurant
@restaurants.route('/restaurants/<int:restaurant_id>/settings')
@login_required
def restaurant_settings(restaurant_id): 
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    hours = get_hours(restaurant_id)
    name = None
    path = f"C:/Users/Gordon Li/Desktop/restaurant_reviews/reviews/static/restaurant/{restaurant_id}"
    if os.path.exists(path):
        name = logo_name_finder(path)
    return render_template('restaurant_settings.html', restaurant=restaurant, hours=hours, name=name)

# Edits the address if user is the restaurant
@restaurants.route('/restaurants/<int:restaurant_id>/address', methods=['GET', 'POST'])
@login_required
def restaurant_address(restaurant_id):
    if (current_user.restaurant_id != restaurant_id):
        return redirect(url_for('main.home'))
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    form = restaurant_address_form()
    if form.validate_on_submit(): 
        restaurant.address = form.address.data
        db.session.commit() 
        return redirect(url_for('restaurants.restaurant_settings', restaurant_id=restaurant_id))
    return render_template('restaurant_address.html', form=form, restaurant=restaurant)

# Edits the phone number if user is the restaurant
@restaurants.route('/restaurants/<int:restaurant_id>/phone', methods=['GET', 'POST'])
@login_required
def restaurant_phone(restaurant_id): 
    if (current_user.restaurant_id != restaurant_id):
        return redirect(url_for('main.home'))
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    form=restaurant_phone_form()
    if form.validate_on_submit(): 
        city = get_city(restaurant.address)
        phone_number = valid_phone_number(form.phone_number.data, city)
        restaurant.phone_number = phone_number
        db.session.commit()
        return redirect(url_for('restaurants.restaurant_settings', restaurant_id=restaurant_id))
    return render_template('restaurant_phone.html', form=form, restaurant=restaurant)

# Edits the hours if user is the restaurant
@restaurants.route('/restaurants/<int:restaurant_id>/hours', methods=['GET', 'POST'])
@login_required
def restaurant_hours(restaurant_id): 
    if (current_user.restaurant_id != restaurant_id):
        return redirect(url_for('main.home'))
    form = restaurant_hour_form()
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    if form.validate_on_submit(): 
        if (restaurant.hour == False):
            monday_hours = RestaurantHours(
                day='Monday',
                morning=form.monday_morning.data, morning_start=form.monday_morning_open.data, morning_end=form.monday_morning_close.data,
                night=form.monday_evening.data, night_start=form.monday_evening_open.data, night_end=form.monday_evening_close.data,
                restaurant_id=restaurant_id
            )
            tuesday_hours = RestaurantHours(
                day='Tuesday',
                morning=form.tuesday_morning.data, morning_start=form.tuesday_morning_open.data, morning_end=form.tuesday_morning_close.data,
                night=form.tuesday_evening.data, night_start=form.tuesday_evening_open.data, night_end=form.tuesday_evening_close.data,
                restaurant_id=restaurant_id
            )
            wednesday_hours = RestaurantHours(
                day='Wednesday',
                morning=form.wednesday_morning.data, morning_start=form.wednesday_morning_open.data, morning_end=form.wednesday_morning_close.data,
                night=form.wednesday_evening.data, night_start=form.wednesday_evening_open.data, night_end=form.wednesday_evening_close.data,
                restaurant_id=restaurant_id
            )
            thursday_hours = RestaurantHours(
                day='Thursday',
                morning=form.thursday_morning.data, morning_start=form.thursday_morning_open.data, morning_end=form.thursday_morning_close.data,
                night=form.thursday_evening.data, night_start=form.thursday_evening_open.data, night_end=form.thursday_evening_close.data,
                restaurant_id=restaurant_id
            )
            friday_hours = RestaurantHours(
                day='Friday',
                morning=form.friday_morning.data, morning_start=form.friday_morning_open.data, morning_end=form.friday_morning_close.data,
                night=form.friday_evening.data, night_start=form.friday_evening_open.data, night_end=form.friday_evening_close.data,
                restaurant_id=restaurant_id
            )
            saturday_hours = RestaurantHours(
                day='Saturday',
                morning=form.saturday_morning.data, morning_start=form.saturday_morning_open.data, morning_end=form.saturday_morning_close.data,
                night=form.saturday_evening.data, night_start=form.saturday_evening_open.data, night_end=form.saturday_evening_close.data,
                restaurant_id=restaurant_id
            )
            sunday_hours = RestaurantHours(
                day='Sunday',
                morning=form.sunday_morning.data, morning_start=form.sunday_morning_open.data, morning_end=form.sunday_morning_close.data,
                night=form.sunday_evening.data, night_start=form.sunday_evening_open.data, night_end=form.sunday_evening_close.data,
                restaurant_id=restaurant_id
            )
            db.session.add(monday_hours)
            db.session.add(tuesday_hours)
            db.session.add(wednesday_hours)
            db.session.add(thursday_hours)
            db.session.add(friday_hours)
            db.session.add(saturday_hours)
            db.session.add(sunday_hours)
            restaurant.hour = True
            db.session.commit()
        else: 
            # Monday
            monday_hours = RestaurantHours.query.filter_by(restaurant_id=restaurant_id, day='Monday').first()
            monday_hours.morning = form.monday_morning.data
            monday_hours.morning_start = form.monday_morning_open.data
            monday_hours.morning_end = form.monday_morning_close.data
            monday_hours.night = form.monday_evening.data
            monday_hours.night_start = form.monday_evening_open.data
            monday_hours.night_end = form.monday_evening_close.data
            # Tuesday
            tuesday_hours = RestaurantHours.query.filter_by(restaurant_id=restaurant_id, day='Tuesday').first()
            tuesday_hours.morning = form.tuesday_morning.data
            tuesday_hours.morning_start = form.tuesday_morning_open.data
            tuesday_hours.morning_end = form.tuesday_morning_close.data
            tuesday_hours.night = form.tuesday_evening.data
            tuesday_hours.night_start = form.tuesday_evening_open.data
            tuesday_hours.night_end = form.tuesday_evening_close.data
            # Wednesday
            wednesday_hours = RestaurantHours.query.filter_by(restaurant_id=restaurant_id, day='Wednesday').first()
            wednesday_hours.morning = form.wednesday_morning.data
            wednesday_hours.morning_start = form.wednesday_morning_open.data
            wednesday_hours.morning_end = form.wednesday_morning_close.data
            wednesday_hours.night = form.wednesday_evening.data
            wednesday_hours.night_start = form.wednesday_evening_open.data
            wednesday_hours.night_end = form.wednesday_evening_close.data
            # Thursday
            thursday_hours = RestaurantHours.query.filter_by(restaurant_id=restaurant_id, day='Thursday').first()
            thursday_hours.morning = form.thursday_morning.data
            thursday_hours.morning_start = form.thursday_morning_open.data
            thursday_hours.morning_end = form.thursday_morning_close.data
            thursday_hours.night = form.thursday_evening.data
            thursday_hours.night_start = form.thursday_evening_open.data
            thursday_hours.night_end = form.thursday_evening_close.data
            # Friday
            friday_hours = RestaurantHours.query.filter_by(restaurant_id=restaurant_id, day='Friday').first()
            friday_hours.morning = form.friday_morning.data
            friday_hours.morning_start = form.friday_morning_open.data
            friday_hours.morning_end = form.friday_morning_close.data
            friday_hours.night = form.friday_evening.data
            friday_hours.night_start = form.friday_evening_open.data
            friday_hours.night_end = form.friday_evening_close.data
            # Saturday
            saturday_hours = RestaurantHours.query.filter_by(restaurant_id=restaurant_id, day='Saturday').first()
            saturday_hours.morning = form.saturday_morning.data
            saturday_hours.morning_start = form.saturday_morning_open.data
            saturday_hours.morning_end = form.saturday_morning_close.data
            saturday_hours.night = form.saturday_evening.data
            saturday_hours.night_start = form.saturday_evening_open.data
            saturday_hours.night_end = form.saturday_evening_close.data
            # Sunday
            sunday_hours = RestaurantHours.query.filter_by(restaurant_id=restaurant_id, day='Sunday').first()
            sunday_hours.morning = form.sunday_morning.data
            sunday_hours.morning_start = form.sunday_morning_open.data
            sunday_hours.morning_end = form.sunday_morning_close.data
            sunday_hours.night = form.sunday_evening.data
            sunday_hours.night_start = form.sunday_evening_open.data
            sunday_hours.night_end = form.sunday_evening_close.data
            db.session.commit()
        return redirect(url_for('restaurants.restaurant_settings', restaurant_id=restaurant_id))
    return render_template('restaurant_hours.html', form=form, restaurant=restaurant)

# Edits the phone number if user is the restaurant
@restaurants.route('/restaurants/<int:restaurant_id>/logo', methods=['GET', 'POST'])
@login_required
def restaurant_logo(restaurant_id): 
    if (current_user.restaurant_id != restaurant_id):
        return redirect(url_for('main.home'))
    form = restaurant_logo_form()
    name = None
    path = f"C:/Users/Gordon Li/Desktop/restaurant_reviews/reviews/static/restaurant/{restaurant_id}"
    if os.path.exists(path):
        name = logo_name_finder(path)
    if form.validate_on_submit():
        path = directory_exists('restaurant', restaurant_id)
        file = form.logo.data
        new_filename = transform_name('logo', file.filename)
        logo_remover("logo.", path)
        file.save(os.path.join(path, new_filename))
        return redirect(url_for('restaurants.restaurant_settings', restaurant_id=restaurant_id))
    return render_template('restaurant_logo.html', form=form, name=name)


@restaurants.route('/restaurants/<int:restaurant_id>/dashboard')
@login_required
def restaurant_dashboard(restaurant_id): 
    if (current_user.role == 'restaurant' and current_user.restaurant_id != restaurant_id): 
        return redirect(url_for('restaurants.restaurant_dashboard', restaurant_id = current_user.restaurant_id))
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    colours = ['#F9F9F9', '#E072A4', '#6883BA', '#3D3B8E', '#B0E298']
    restaurant_ratings = get_restaurant_rating_scores(restaurant_id)
    restaurant_ratings_l, restaurant_ratings_v = convert_dict_ratings(restaurant_ratings)
    restaurant_ratings_labels = [str(x) for x in restaurant_ratings_l]
    restaurant_ratings_values = [str(x) for x in restaurant_ratings_v]
    dish_ratings = get_dish_rating_scores(restaurant_id)
    dish_ratings_l, dish_ratings_v = convert_dict_ratings(restaurant_ratings)
    dish_ratings_labels = [str(x) for x in restaurant_ratings_l]
    dish_ratings_values = [str(x) for x in restaurant_ratings_v]
    labels_top_3, rating_top_3 = get_top_3(restaurant_id)
    ratings_top_3 = [str(x) for x in rating_top_3]
    labels_worst_3, rating_worst_3 = get_worst_3(restaurant_id)
    ratings_worst_3 = [str(x) for x in rating_worst_3]
    top_3_colors = colours[:len(labels_top_3)]
    top_3_exists = True
    if (len(labels_top_3) == 0): 
        top_3_exists = False
    worst_3_colors = colours[:len(labels_worst_3)]
    worst_3_exists = True
    if (len(labels_worst_3) == 0): 
        worst_3_exists = False
    popular_3_labels, popular_3_values = get_popular_3(restaurant_id)
    popular_3_exists = True
    if (len(popular_3_labels) == 0): 
        popular_3_exists = False
    popular_3_colors = colours[:len(popular_3_labels)]
    avg = get_avg_cost(restaurant_id)
    past_date_one_month = datetime.now() - relativedelta(months=1)
    count = get_posts_month_restaurant(restaurant_id, past_date_one_month)
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    return render_template('restaurant_dashboard.html', name = restaurant.name.upper(),
        restaurant_ratings_labels=restaurant_ratings_labels, restaurant_ratings_values=restaurant_ratings_values,
        dish_ratings_labels=dish_ratings_labels, dish_ratings_values=dish_ratings_values,
        labels_top_3=labels_top_3, ratings_top_3=ratings_top_3, top_3_colors=top_3_colors, top_3_exists=top_3_exists,
        labels_worst_3=labels_worst_3, ratings_worst_3=ratings_worst_3, worst_3_colors=worst_3_colors, worst_3_exists=worst_3_exists,
        popular_3_labels=popular_3_labels, popular_3_values=popular_3_values, popular_3_colors=popular_3_colors, \
        popular_3_exists=popular_3_exists, avg=avg, count=count, colors=colours)

@restaurants.route('/reply/<int:post_id>', methods=['GET', 'POST'])
@login_required
def reply_posts_by_id(post_id):
    form = restaurant_comments_form()
    if (current_user.role != 'restaurant'):
        return redirect(url_for('main.home'))
    with app.app_context():
        post_list_draft = get_posts_v2(post_id)
        post_list = [] 
        for element in post_list_draft:
            inner_list = []
            for values in element: 
                inner_list.append(values)
            user_id = inner_list[12]
            name = None
            path = f"C:/Users/Gordon Li/Desktop/restaurant_reviews/reviews/static/user/{user_id}"
            if os.path.exists(path):
                name =  os.listdir(path)[0]
            inner_list.append(name)
            post_list.append(inner_list)
        print(post_list)
        if form.validate_on_submit(): 
            with app.app_context(): 
                restaurant_comments = RestaurantComment(comment = form.comment.data, user_id=current_user.id, post_id=post_id)
                post = Post.query.get_or_404(post_id)
                post.reply = True
                print(post.reply)
                db.session.add(restaurant_comments)
                db.session.commit()
            return redirect(url_for('restaurants.restaurant', restaurant_id=current_user.restaurant_id))
        return render_template('reply_post.html', form=form, post=post_list[0])