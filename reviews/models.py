from reviews import db, app, ma
from datetime import datetime, date
from flask_login import UserMixin
from reviews import login_manager

class User(db.Model, UserMixin): 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    date_joined = db.Column(db.DateTime, nullable=False, default=date.today)
    role = db.Column(db.String(20), nullable=False, default='regular')
    restaurant_id = db.Column(db.Integer, unique=True, nullable=True)
    posts = db.relationship('Post', backref='user', lazy=True)
    feedback = db.relationship('Feedback', backref='user', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)
    restaurantuser = db.relationship('RestaurantUser', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.password}', '{self.location}', '{self.date_joined}')"


class UserSchema(ma.Schema): 
    class Meta: 
        fields = ("username", "email", "location", "date_joined", "role")

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable = False)
    cuisine = db.Column(db.String(20), nullable = False)
    address = db.Column(db.String(120), nullable = False)
    phone_number = db.Column(db.String(20), nullable = False)
    hour = db.Column(db.Boolean, default=False)
    restauranthours = db.relationship('RestaurantHours', backref = 'restaurant', lazy=True)
    posts = db.relationship('Post', backref='restaurant', lazy=True)

    def __repr__(self):
        return f"Restuarant('{self.name}', '{self.cuisine}', '{self.address}', '{self.phone_number}')"
    
class RestaurantHours(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(40), nullable=False)
    morning = db.Column(db.String(40), nullable=False)
    night = db.Column(db.String(40), nullable=False)
    morning_start = db.Column(db.Time, nullable=False)
    morning_end = db.Column(db.Time, nullable=False)
    night_start = db.Column(db.Time, nullable=False)
    night_end = db.Column(db.Time, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    
    def __repr__(self):
        return f"RestaurantHours('{self.day}', '{self.morning}', '{self.morning_start}', '{self.morning_end}', \
            '{self.night}', '{self.night_start}', '{self.night_end}'"


class Dish(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable = False)
    posts = db.relationship('Post', backref='dish', lazy=True)
    dishtype_id = db.Column(db.Integer, db.ForeignKey('dish_type.id'), nullable=False)

    def __repr__(self):
        return f"Dish('{self.name}')"

class DishType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(120), nullable=False)
    overview = db.Column(db.Text, nullable=True)
    dishes = db.relationship('Dish', backref='dishtype', lazy=True)

class Post(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    restaurant_rating = db.Column(db.Integer, nullable = False) 
    dish_rating = db.Column(db.Integer, nullable = False)
    cost =  db.Column(db.Integer, nullable = False)
    value = db.Column(db.Integer, nullable = False)
    size = db.Column(db.String(20), nullable = False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    upvotes = db.Column(db.Integer, nullable=False, default=0)
    reply = db.Column(db.Boolean, default=False)
    likes = db.relationship('Like', backref='post', lazy=True)
    comments = db.relationship('RestaurantComment', backref='post', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    dish_id = db.Column(db.Integer, db.ForeignKey('dish.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.restaurant_rating}', '{self.dish_rating}', '{self.cost}', '{self.content}', '{self.date_posted}')"


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __repr__(self):
        return f"Like('{self.user_id}', '{self.post_id})"

class RestaurantComment(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"RestaurantComments('{self.user_id}', '{self.comment}')"

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    solved = db.Column(db.String(20), nullable=False, default="Unsolved")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    feedbackcomments = db.relationship('FeedbackComments', backref='feedback', lazy=True)
    def __repr__(self):
        return f"Feedback('{self.title}', '{self.category}', '{self.content}')"

class FeedbackComments(db.Model): 
    id = db.Column(db.Integer, primary_key = True)
    comment = db.Column(db.Text, nullable = False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'), nullable=False)

    def __repr__(self): 
        return f"Feedback_Comments({self.comment})"

class RestaurantUser(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120), nullable=False)
    restaurant = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    info = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Unsolved")
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurantusercomments = db.relationship('RestaurantUserComments', backref='restaurantuser', lazy=True)

    def __repr__(self): 
        return f"RestaurantUser('{self.name}', '{self.restaurant}, '{self.address}')"

class RestaurantUserComments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=False)
    post_time = db.Column(db.DateTime, nullable=False)
    restaurantuser_id = db.Column(db.Integer, db.ForeignKey('restaurant_user.id'), nullable=False)

    def __repr__(self): 
        return f"RestaurantUserComments('{self.comment}', '{self.post_time}')"



