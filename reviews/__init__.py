
from flask import Flask
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

UPLOAD_FOLDER = 'C:/Users/Gordon Li/Desktop/restaurant_reviews/reviews/static'

app = Flask(__name__)
ma = Marshmallow(app)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['UPLOADED_IMAGES_DEST'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0414798688aB@localhost:5432/reviews_db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from reviews.main.routes import main
from reviews.users.routes import users
from reviews.privileges.routes import privileges
from reviews.posts.routes import posts
from reviews.restaurants.routes import restaurants
from reviews.dishes.routes import dishes
from reviews.feedbacks.routes import feedbacks
from reviews.applications.routes import applications
app.register_blueprint(main)
app.register_blueprint(users)
app.register_blueprint(privileges)
app.register_blueprint(posts)
app.register_blueprint(restaurants)
app.register_blueprint(dishes)
app.register_blueprint(feedbacks)
app.register_blueprint(applications)

from reviews import api