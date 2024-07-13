from flask import Flask, jsonify, make_response, request, url_for
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from waitress import serve


from models import db, UserModel, ProductModel, cartModel, cartItemModel, OrderModel, OrderItemModel, ReviewModel

# create a Flask application object
app = Flask(__name__)

# configure a database connection to the local file app.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'

# disable modification tracking to use less memory
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
api = Api(app)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'UserModel': UserModel, 'ProductModel': ProductModel, 'cartModel': cartModel, 'cartItemModel': cartItemModel, 'OrderModel': OrderModel, 'OrderItemModel': OrderItemModel, 'ReviewModel': ReviewModel}



#resource class
class Home(Resource):
    def get(self):
        response_dict = {
            "message": "Welcome to ShoeGalore API. Here are the available resources: /users, /products, /carts, /cart_items, /orders, /order_items, /reviews",
        }
        return response_dict, 200

api.add_resource(Home, '/')
#User resource class
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

        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

            return {"error": "User with this username or email already exists"}, 400    

        return new_user.to_dict(), 201
    #get all users
    def get(self):
        users = UserModel.query.all()
        return[user.to_dict() for user in users], 200
api.add_resource(UserResource, '/users')  

class UserResourceById(Resource):
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
    
api.add_resource(UserResourceById, '/users/<int:user_id>')   

#Product resource class
class ProductResource(Resource):
    #get all products
    def get(self):
        products = ProductModel.query.all()
        return [product.to_dict() for product in products], 200

    #create product
    def post(self):
        data = request.get_json()
        if not data or not all(key in data for key in ("name", "price", "stock")):
            return {"error": "Missing required fields"}, 400

        name = data["name"]
        price = data["price"]
        stock = data["stock"]

        if price < 0 or stock < 0:
            return {"error": "Price and stock must be non-negative"}, 400

        new_product = ProductModel(name=name, price=price, stock=stock)
        try:
            db.session.add(new_product)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"error": "Product already exists"}, 400

        return new_product.to_dict(), 201

    #update product
    def put(self, product_id):
        data = request.get_json()
        if not data or not all(key in data for key in ("name", "price", "stock")):
            return {"error": "Missing required fields"}, 400
        product = ProductModel.query.get(product_id)
        if not product:
            return {"error": "Product not found"}, 404
        product.name = data["name"]
        product.price = data["price"]
        product.stock = data["stock"]
        db.session.commit()
        return product.to_dict(), 200

    #delete product
    def delete(self, product_id):
        product = ProductModel.query.get(product_id)
        if not product:
            return {"error": "Product not found"}, 404
        db.session.delete(product)
        db.session.commit()
        return {"message": "Product deleted successfully"}, 200
    
api.add_resource(ProductResource,'/products')

class ProductResourceById(Resource):
    
    #get product by id
    def get(self, product_id):
        product = ProductModel.query.get(product_id)
        if not product:
            return {"error": "Product not found"}, 404
        return product.to_dict(), 200

    #delete product by id
    def delete(self, product_id):
        product = ProductModel.query.get(product_id)
        if not product:
            return {"error": "Product not found"}, 404
        db.session.delete(product)
        db.session.commit()
        return {"message": "Product deleted successfully"}, 200

api.add_resource(ProductResourceById,'/products/<int:product_id>')

#Cart resource class
class CartResource(Resource):
    #create cart
    def post(self):
        data = request.get_json()
        if not data or not all(key in data for key in ("user_id", "product_id", "quantity")):
            return {"error": "Missing required fields"}, 400

        quantity = data["quantity"]
        if quantity <= 0:
            return {"error": "Quantity must be greater than zero"}, 400

        new_cart = cartModel(user_id=data["user_id"], product_id=data["product_id"], quantity=quantity)
        db.session.add(new_cart)
        db.session.commit()

        return new_cart.to_dict(), 201
    #get all carts
    def get(self):
        carts = cartModel.query.all()
        return [cart.to_dict() for cart in carts], 200
    
api.add_resource(CartResource,'/carts')    

class CartResourceById(Resource):    
    #get cart by id
    def get(self, cart_id):
        cart = cartModel.query.get(cart_id)
        if not cart:
            return {"error": "Cart not found"}, 404
        return cart.to_dict(), 200

    #update cart
    def put(self, cart_id):
        data = request.get_json()
        if not data or "quantity" not in data:
            return {"error": "Missing required fields"}, 400

        cart = cartModel.query.get(cart_id)
        if not cart:
            return {"error": "Cart not found"}, 404

        quantity = data["quantity"]
        if quantity <= 0:
            return {"error": "Quantity must be greater than zero"}, 400

        cart.quantity = quantity
        db.session.commit()
        return cart.to_dict(), 200

    #delete cart
    def delete(self, cart_id):
        cart = cartModel.query.get(cart_id)
        if not cart:
            return {"error": "Cart not found"}, 404
        db.session.delete(cart)
        db.session.commit()
        return {"message": "Cart deleted successfully"}, 200

api.add_resource(CartResourceById, '/carts/<int:cart_id>')

#CartItem resource class
class CartItemResource(Resource):
    # Get all cart items
    def get(self):
        cart_items = cartItemModel.query.all()
        return [cart_item.to_dict() for cart_item in cart_items], 200

    # Add a new cart item
    def post(self):
        data = request.get_json()
        if not data or not all(key in data for key in ("cart_id", "product_id", "quantity")):
            return {"error": "Missing required fields"}, 400

        quantity = data["quantity"]
        if quantity <= 0:
            return {"error": "Quantity must be greater than zero"}, 400

        new_cart_item = cartItemModel(cart_id=data["cart_id"], product_id=data["product_id"], quantity=quantity)
        db.session.add(new_cart_item)
        db.session.commit()

        return new_cart_item.to_dict(), 201

api.add_resource(CartItemResource,'/cart_items')

# Separate resource for handling individual cart items by ID
class CartItemByIdResource(Resource):
    # Get cart item by ID
    def get(self, cart_item_id):
        cart_item = cartItemModel.query.get(cart_item_id)
        if not cart_item:
            return {"error": "Cart item not found"}, 404
        return cart_item.to_dict(), 200
    
    #add cart item
    def post(self):
        data = request.get_json()
        if not data or not all(key in data for key in ("cart_id", "product_id", "quantity")):
            return {"error": "Missing required fields"}, 400
        new_cart_item = cartItemModel(cart_id=data["cart_id"], product_id=data["product_id"], quantity=data["quantity"])
        db.session.add(new_cart_item)
        db.session.commit()
        return new_cart_item.to_dict(), 201

    #update cart item
    def put(self, cart_item_id):
        data = request.get_json()
        if not data or "quantity" not in data:
            return {"error": "Missing required fields"}, 400

        cart_item = cartItemModel.query.get(cart_item_id)
        if not cart_item:
            return {"error": "Cart item not found"}, 404

        quantity = data["quantity"]
        if quantity <= 0:
            return {"error": "Quantity must be greater than zero"}, 400

        cart_item.quantity = quantity
        db.session.commit()
        return cart_item.to_dict(), 200

    #delete cart item
    def delete(self, cart_item_id):
        cart_item = cartItemModel.query.get(cart_item_id)
        if not cart_item:
            return {"error": "Cart item not found"}, 404
        db.session.delete(cart_item)
        db.session.commit()
        return {"message": "Cart item deleted successfully"}, 200
    
api.add_resource(CartItemByIdResource, '/cart_items/<int:cart_item_id>')  


# Order resource class
class OrderResource(Resource):
    # Get all orders
    def get(self):
        orders = OrderModel.query.all()
        return [order.to_dict() for order in orders], 200

    # Create an order
    def post(self):
        data = request.get_json()
        if not data or not all(key in data for key in ("user_id", "product_id", "quantity")):
            return {"error": "Missing required fields"}, 400

        quantity = data["quantity"]
        if quantity <= 0:
            return {"error": "Quantity must be greater than zero"}, 400

        new_order = OrderModel(user_id=data["user_id"], product_id=data["product_id"], quantity=quantity)
        db.session.add(new_order)
        db.session.commit()

        return new_order.to_dict(), 201

api.add_resource(OrderResource,'/orders')

# Separate resource for handling individual orders by ID
class OrderByIdResource(Resource):
    # Get order by ID
    def get(self, order_id):
        order = OrderModel.query.get(order_id)
        if not order:
            return {"error": "Order not found"}, 404
        return order.to_dict(), 200

    # Update order
    def put(self, order_id):
        data = request.get_json()
        if not data or "quantity" not in data:
            return {"error": "Missing required fields"}, 400

        order = OrderModel.query.get(order_id)
        if not order:
            return {"error": "Order not found"}, 404

        quantity = data["quantity"]
        if quantity <= 0:
            return {"error": "Quantity must be greater than zero"}, 400

        order.quantity = quantity
        db.session.commit()
        return order.to_dict(), 200


    # Delete order
    def delete(self, order_id):
        order = OrderModel.query.get(order_id)
        if not order:
            return {"error": "Order not found"}, 404
        db.session.delete(order)
        db.session.commit()
        return {"message": "Order deleted successfully"}, 200

api.add_resource(OrderByIdResource, '/orders/<int:order_id>')

#order item resource class
class OrderItemResource(Resource):
    # Get all order items
    def get(self):
        order_items = OrderItemModel.query.all()
        return [order_item.to_dict() for order_item in order_items], 200

    # Create an order item
    def post(self):
        data = request.get_json()
        if not data or not all(key in data for key in ("order_id", "product_id", "quantity")):
            return {"error": "Missing required fields"}, 400

        quantity = data["quantity"]
        if quantity <= 0:
            return {"error": "Quantity must be greater than zero"}, 400

        new_order_item = OrderItemModel(order_id=data["order_id"], product_id=data["product_id"], quantity=quantity)
        db.session.add(new_order_item)
        db.session.commit()

        return new_order_item.to_dict(), 201

api.add_resource(OrderItemResource,'/order_items')


# Separate resource for handling individual order items by ID
class OrderItemByIdResource(Resource):
    # Get order item by ID
    def get(self, order_item_id):
        order_item = OrderItemModel.query.get(order_item_id)
        if not order_item:
            return {"error": "Order item not found"}, 404
        return order_item.to_dict(), 200

    # Update order item
    def put(self, order_item_id):
        data = request.get_json()
        if not data or "quantity" not in data:
            return {"error": "Missing required fields"}, 400

        order_item = OrderItemModel.query.get(order_item_id)
        if not order_item:
            return {"error": "Order item not found"}, 404

        quantity = data["quantity"]
        if quantity <= 0:
            return {"error": "Quantity must be greater than zero"}, 400

        order_item.quantity = quantity
        db.session.commit()
        return order_item.to_dict(), 200

    # Delete order item
    def delete(self, order_item_id):
        order_item = OrderItemModel.query.get(order_item_id)
        if not order_item:
            return {"error": "Order item not found"}, 404
        db.session.delete(order_item)
        db.session.commit()
        return {"message": "Order item deleted successfully"}, 200
    
api.add_resource(OrderItemByIdResource, '/order_items/<int:order_item_id>')

#review resource class
class ReviewResource(Resource):
    # Get all reviews
    def get(self):
        reviews = ReviewModel.query.all()
        return [review.to_dict() for review in reviews], 200

    # Create a review
    def post(self):
        data = request.get_json()
        if not data or not all(key in data for key in ("user_id", "product_id", "rating", "comment")):
            return {"error": "Missing required fields"}, 400

        rating = data["rating"]
        if not (1 <= rating <= 5):
            return {"error": "Rating must be between 1 and 5"}, 400

        new_review = ReviewModel(user_id=data["user_id"], product_id=data["product_id"], rating=rating, comment=data["comment"])
        db.session.add(new_review)
        db.session.commit()

        return new_review.to_dict(), 201
    

api.add_resource(ReviewResource,'/reviews')


# Separate resource for handling individual reviews by ID
class ReviewByIdResource(Resource):
    # Get review by ID
    def get(self, review_id):
        review = ReviewModel.query.get(review_id)
        if not review:
            return {"error": "Review not found"}, 404
        return review.to_dict(), 200

    # Update review
    def put(self, review_id):
        data = request.get_json()
        if not data or not all(key in data for key in ("rating", "comment")):
            return {"error": "Missing required fields"}, 400

        review = ReviewModel.query.get(review_id)
        if not review:
            return {"error": "Review not found"}, 404

        rating = data["rating"]
        if not (1 <= rating <= 5):
            return {"error": "Rating must be between 1 and 5"}, 400

        review.rating = rating
        review.comment = data["comment"]
        db.session.commit()
        return review.to_dict(), 200
    # Delete review
    def delete(self, review_id):
        review = ReviewModel.query.get(review_id)
        if not review:
            return {"error": "Review not found"}, 404
        db.session.delete(review)
        db.session.commit()
        return {"message": "Review deleted successfully"}, 200
    
api.add_resource(ReviewByIdResource, '/reviews/<int:review_id>')











if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=50200, threads=4)