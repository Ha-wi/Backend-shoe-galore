from flask import Flask, jsonify, make_response, request, url_for
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
    #create user in database
    def post(self):
        data = request.get_json()

        if not data or not all(key in data for key in ("username", "email", "password")):
            return {"error": "Missing required fields"}, 400

        username = data["username"]
        email = data["email"]
        password = data["password"]

        # Check if the user already exists
        if UserModel.query.filter((UserModel.username == username) | (UserModel.email == email)).first():
            return {"error": "User with this username or email already exists"}, 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = UserModel(username=username, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        return new_user.to_dict(), 201
    #get all users
    def get(self):
        users = UserModel.query.all()
        return[user.to_dict() for user in users], 200
    #get user by id
    def get(self, user_id):
        user = UserModel.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404
        return user.to_dict(), 200
    #update user
    def put(self, user_id):
        data = request.get_json()
        if not data or not all(key in data for key in ("username", "email", "password")):
            return {"error": "Missing required fields"}, 400
        user = UserModel.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404
        user.username = data["username"]
        user.email = data["email"]
        user.password = data["password"]
        db.session.commit()
        return user.to_dict(), 200
    
    #delete user 
    def delete(self, user_id):
        user = UserModel.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404

        db.session.delete(user)
        db.session.commit()

        return {"message": "User deleted successfully"}, 200
    
api.add_resource(UserResource, '/users', '/users/<int:user_id>')   

    


# Utility Resource to list all routes
class ListRoutes(Resource):
    def get(self):
        import urllib
        output = []
        for rule in app.url_map.iter_rules():
            options = {}
            for arg in rule.arguments:
                options[arg] = "[{0}]".format(arg)

            methods = ','.join(rule.methods)
            url = url_for(rule.endpoint, **options)
            line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
            output.append(line)

        for line in sorted(output):
            print(line)
        return jsonify(routes=sorted(output))

api.add_resource(ListRoutes, '/routes')

if __name__ == '__main__':
    app.run(port=5000, debug=True)