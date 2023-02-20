import os
from flask import render_template, url_for, redirect, Blueprint
from flask_login import current_user, login_required
from reviews import app, db
from reviews.models import Restaurant, User, DishType, Dish, Post
from reviews.posts.forms import post_reviews_form, edit_post_form
from reviews.posts.helper import (
    valid_phone_number, get_dish_overview, directory_exists,
    transform_name, image_resizer, get_my_post, image_adder
)

posts = Blueprint('posts', __name__)

# Posts Review
@posts.route('/post_review', methods=['GET', 'POST'])
@login_required
def post_review(): 
    if (current_user.role == 'restaurant' or current_user.role == 'admin'):
        return redirect(url_for('main.home'))
    form = post_reviews_form()
    if form.validate_on_submit():
        with app.app_context(): 
            restaurant = Restaurant.query.filter_by(name=form.restaurant.data, address=form.restaurant_address.data).first()
            if restaurant is None: 
                user = User.query.filter_by(username=current_user.username).first()
                city = user.location
                phone_number = valid_phone_number(form.phone_number.data, city)
                restaurant = Restaurant(name=form.restaurant.data, \
                    cuisine=form.restaurant_cuisine.data, address=form.restaurant_address.data,\
                    phone_number=phone_number)
                db.session.add(restaurant)
                db.session.commit()
            dish_type = DishType.query.filter_by(type=form.dish_type.data).first()
            if (dish_type is None): 
                dishtype, overview = get_dish_overview(form.dish_type.data)
                dish_type = DishType(type = dishtype, overview=overview)
                db.session.add(dish_type)
                db.session.commit()
            dish = Dish.query.filter_by(name=form.dish.data).first()
            if dish is None: 
                dish = Dish(name=form.dish.data, dishtype=dish_type)
                db.session.add(dish)
                db.session.commit()
            post = Post(title=form.title.data, restaurant_rating=form.restaurant_rating.data,\
                    value=form.value.data, size=form.dish_size.data, dish_rating=form.dish_rating.data, cost=form.dish_cost.data,\
                    content=form.content.data, user=current_user, restaurant=restaurant, dish=dish)
            db.session.add(post)
            db.session.commit()
            directory_exists("post", post.id)
            path = f"C:/Users/Gordon Li/Desktop/restaurant_reviews/reviews/static/post/{post.id}"
            file_restaurant = form.restaurant_image.data
            file_dish = form.dish_image.data
            if file_restaurant: 
                new_filename = transform_name('restaurant', file_restaurant.filename)  
                file_restaurant.save(os.path.join(path, new_filename))
                image_resizer(os.path.join(path, new_filename))
            if file_dish: 
                new_filename = transform_name('dish', file_dish.filename)  
                file_dish.save(os.path.join(path, new_filename))
                image_resizer(os.path.join(path, new_filename))
        return redirect(url_for('users.account_info'))
    return render_template('post.html', form=form)

# Get Started on posting
@posts.route('/post_review/get_started')
@login_required
def get_started(): 
    return render_template('get_started.html')

# Edit Post
@posts.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_posts_by_id(post_id):
    post = Post.query.get_or_404(post_id)
    if (post.user_id != current_user.id): 
        return redirect(url_for('main.home'))
    new_list = get_my_post(post_id)
    post_list = image_adder(new_list, 'my_post', current_user.id)
    form = edit_post_form()
    if form.validate_on_submit(): 
        post = Post.query.filter_by(id=post_id).first() 
        if (form.title.data != ''): 
            post.title = form.title.data
        post.restaurant_rating = form.restaurant_rating.data
        post.dish_rating = form.dish_rating.data
        post.cost = form.dish_cost.data
        post.size = form.dish_size.data
        post.value = form.value.data
        if form.content.data != '':
            post.content = form.content.data
        db.session.commit()
        return redirect(url_for('post.edit_posts_by_id', post_id=post_id))
    return render_template('edit_post.html', user_id=current_user.id, review=post_list[0], form=form)