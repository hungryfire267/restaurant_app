
from flask import url_for, render_template, request, flash, redirect, Blueprint
from flask_login import current_user, login_required
from reviews import app, db
from reviews.models import DishType, Post, Like
from reviews.dishes.forms import dish_search_form, dish_form
from reviews.dishes.helper import (
    get_top_3_dishes, get_top_3_restaurants_dishes, get_avg_dish_rating,
    get_dish_images_sql, get_dish_images, get_dish_posts, image_adder
)

dishes = Blueprint('dishes', __name__)

# Search Dishes
@dishes.route('/dishes', methods=['GET', 'POST'])
@login_required
def dish_search(): 
    form = dish_search_form()
    form.dish.choices = []
    for dish in DishType.query.all(): 
        form.dish.choices.append((dish.type, dish.type))
    form.dish.choices = sorted(form.dish.choices)
    dish_type = None
    if form.validate_on_submit(): 
        dish_type = DishType.query.filter_by(type=form.dish.data).first()
    return render_template('dish_search.html', form = form, dish_type=dish_type)

# Get Dish Type information
@dishes.route('/dishes/<int:dish_id>', methods=['GET', 'POST'])
@login_required
def dish(dish_id):
    form = dish_form()
    dish_type = DishType.query.get_or_404(dish_id)
    top_3_list = get_top_3_dishes(dish_id)  
    top_3_restaurants = get_top_3_restaurants_dishes(dish_id)
    avg = get_avg_dish_rating(dish_id)
    form.order.choices = [('', '-'), ('asc,', 'Increasing'), ('desc,', 'Decreasing')]
    post_ids = get_dish_images_sql(dish_id)
    dish_images_unsort = get_dish_images(post_ids)
    dish_images = sorted(dish_images_unsort, key=lambda x: str(x[3] is False))
    dish_posts = []
    statement = None
    if form.validate_on_submit(): 
        if (form.sort.data == '' and form.order.data != ''):
            dish_posts = []
            statement = "You cannot select increasing or decreasing as an order by."
            flash(statement, 'danger')
        elif (form.sort.data != '' and form.order.data == ''): 
            dish_posts = []
            statement = "You must select increasing or decreasing as an order by."
            flash(statement, 'danger')
        else:
            new_posts = get_dish_posts(dish_id, form.dish.data, form.restaurant.data, form.sort.data, form.order.data)
            dish_posts = image_adder(new_posts, 'dish', None)
            statement = "Success"
            flash(statement, 'success')
    else: 
        new_posts = get_dish_posts(dish_id, "", "", "", "")
        dish_posts = image_adder(new_posts, 'dish', None)
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
        return redirect(url_for('dishes.dish', dish_id=dish_id))
    return render_template('dish_profile.html', dish_type=dish_type, top_3 = top_3_list,\
        avg=avg, form=form, dish_posts=dish_posts, statement=statement, top_3_restaurants=top_3_restaurants, dish_images=dish_images)
