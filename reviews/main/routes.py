from datetime import datetime, timedelta
import pytz
import os
import re
from random import sample
from flask import (render_template, request, redirect, url_for, Blueprint)
from flask_login import(current_user, login_required)
from reviews import db, app
from reviews.models import Post, Like, Restaurant
from reviews.main.forms import finder_form
from reviews.main.helper import (
    weather_data, weather_pred, get_dishtype_list, get_images_home,
    get_trending_posts, image_adder, day_choices, location_string, cuisine_string,
    restaurant_recommender, dish_type_string, restaurant_recommender_simplified,
    order_by_average_rating, logo_name_finder
    )

main = Blueprint('main', __name__)

#Gets home page (weather, trending posts, dish overviews)
@main.route("/", methods=['POST', 'GET'])
def home(): 
    if (current_user.is_authenticated):
        timezones = {'Sydney': 'Australia/Sydney', 'Melbourne': 'Australia/Sydney', 
        'Brisbane': 'Australia/Brisbane', 'Perth': 'Australia/Perth', 
        'Adelaide': 'Australia/Adelaide', 'Hobart': 'Australia/Sydney', 'Canberra': 'Australia/Sydney'}
        timezone_user = timezones[current_user.location]
        tz = pytz.timezone(timezone_user)
        time_now = datetime.now(tz)
        hour = time_now.hour
        greeting = None
        if (hour >= 5 and hour < 12):
            greeting = "Good Morning"
        elif (hour >= 12 and hour < 17):
            greeting = "Good Afternoon"
        else: 
            greeting = "Good Evening"
        greeting = greeting + ', ' + current_user.username + '!'
        day_of_week  = time_now.strftime('%A')
        date = time_now.day
        month_name = time_now.strftime('%B')
        date_string = f"{day_of_week}, {date} {month_name}"
        time = time_now.strftime("%I:%M %p").lstrip('0')
        weather_condition_now, weather_degrees_now, weather_wind_now, wind_dir = weather_data(user=current_user)
        min_temp, max_temp, weather_condition = weather_pred(user=current_user, hour=hour)
        dish_types = get_dishtype_list() 
        dish_types_simplified = []
        if (len(dish_types) < 3): 
            for dish in dish_types: 
                dish_types_simplified.append(dish)
        else: 
            dish_types_simplified = sample(dish_types, 3)
        time_now = datetime.now()
        time_3_days_prior = time_now - timedelta(days=3)
        images = sorted(get_images_home(), key=lambda x: str(x[1] is False))
        print(images)
        new_posts = get_trending_posts(time_3_days_prior)
        trending_posts = image_adder(new_posts, 'trending', None)
        if (request.form.get('like') == "1" or request.form.get('dislike') == "-1"):
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
            return redirect(url_for('main.home'))
        return render_template('home_login.html', greeting=greeting, date_string=date_string,
            time=time, weather_condition_now=weather_condition_now, weather_degrees_now=weather_degrees_now,
            weather_wind_now=weather_wind_now, wind_dir=wind_dir, hour=hour, min_temp=min_temp, max_temp=max_temp,
            weather_condition=weather_condition, dish_types=dish_types_simplified, images=images, trending_posts=trending_posts)
    return render_template('home.html')

# Get Restaurant Recommendations
@main.route('/finder', methods=['GET', 'POST'])
def recommender(): 
    form = finder_form()
    form.date.choices = day_choices()
    outer_list = None
    if form.validate_on_submit(): 
        location_list = re.split(', ', form.location.data)
        location_strings = location_string(location_list)
        print(location_strings)
        cuisine_strings = cuisine_string(form.cuisine.data)
        new_list = restaurant_recommender(form.date.data, form.time.data, location_strings, cuisine_strings)
        print(new_list)
        final_list = []
        dish_type = dish_type_string(form.dish_type.data)
        for element in new_list:
           if (restaurant_recommender_simplified(element, dish_type) == True): 
               final_list.append(element)
        avg_rating_dict = {}
        for restaurant_id in final_list: 
            avg_rating_dict[restaurant_id] = order_by_average_rating(restaurant_id)
        print(avg_rating_dict)
        sort_restaurant = sorted(avg_rating_dict.items(), key=lambda x: x[1], reverse=True)
        outer_list = []
        for element in sort_restaurant: 
            restaurant = Restaurant.query.filter_by(id=element[0]).first()
            path = f"C:/Users/Gordon Li/Desktop/restaurant_reviews/reviews/static/restaurant/{element[0]}"
            logo_name = None
            if (os.path.exists(path)):
                logo_name = logo_name_finder(path)
            print(logo_name)
            inner_list = [restaurant.id, restaurant.name, restaurant.cuisine, restaurant.address, restaurant.phone_number, 
                            restaurant.hour, logo_name, avg_rating_dict[restaurant.id]]
            outer_list.append(inner_list)
    return render_template('recommender.html', form=form, outer_list=outer_list)