from flask import Flask, jsonify, make_response, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_bcrypt import Bcrypt

from models import db, UserModel, Product 

# create a Flask application object
app = Flask(__name__)

# configure a database connection to the local file app.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'

# disable modification tracking to use less memory
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# create a Migrate object to manage schema modifications
migrate = Migrate(app, db)

# create a Bcrypt object to hash passwords
bcrypt = Bcrypt(app)

# initialize the Flask application to use the database
db.init_app(app)

api = Api(app)

#resource class
class Home(Resource):
    def get(self):
        response_dict = {
            "message": "Welcome to the Newsletter RESTful API",
        }
        return response_dict, 200

    
    

api.add_resource(Home, '/')

class UserResource(Resource):
    def get(self):
        users = UserModel.query.all()
        return[user.to_dict() for user in users], 200
    

    def post(self):
        data = request.get_json()
        new_user = UserModel(username=data['username'], email=data['email'])
        db.session.add(new_user)
        db.session.commit()
        return new_user.to_dict(), 201 

         
    
api.add_resource(UserResource, '/users')



if __name__ == '__main__':
    app.run(port=5555, debug=True)