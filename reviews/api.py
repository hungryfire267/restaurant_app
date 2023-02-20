from reviews.models import User, UserSchema
from reviews import app
from flask_restful import Resource, Api
api = Api(app)

users_schema = UserSchema(many=True)
with app.app_context():
    all_users = User.query.all()
    users = users_schema.dump(all_users)

class User_api(Resource): 
    def get(self, user_id): 
        if (user_id == 'all'):
            return users
        else: 
            return users[int(user_id)-1]


api.add_resource(User_api, '/api/user/<user_id>')