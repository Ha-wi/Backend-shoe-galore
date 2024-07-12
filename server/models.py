#models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin

# import the Bcrypt extension to hash passwords securely
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
# contains definitions of tables and associated schema constructs
# read more about Metadata using the link at the bottom of the page
metadata = MetaData()

# create the Flask SQLAlchemy extension
db = SQLAlchemy(metadata=metadata)

# define a model class by inheriting from db.Model.
class UserModel(db.Model, SerializerMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    cart = db.relationship('cartModel', backref='user', lazy=True)
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)    
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            
        }
        
    def __repr__(self):
        return '<User %r>' % self.username

class ProductModel(db.Model, SerializerMixin):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    cart = db.relationship('cartModel', backref='product', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price
        }

    def __init__(self, name, price, stock=None, user_id=None, product_id=None, quantity=None):
        self.name = name
        self.price = price
        self.stock = stock
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity

    def __repr__(self):
        return f'<Product {self.name}>'
 

class cartModel(db.Model):
    __tablename__ = 'cart'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def __init__(self, user_id, product_id, quantity):
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity

    def to_dict(self):
        return{
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'quantity': self.quantity
        }
        

    def __repr__(self):
        return '<Cart %r>' % self.id

class cartItemModel(db.Model):
    __tablename__ = 'cart_item'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return{
            'id': self.id,
            'cart_id': self.cart_id,
            'product_id': self.product_id,
            'quantity': self.quantity
        }

    def __init__(self, cart_id, product_id, quantity):
        self.cart_id = cart_id
        self.product_id = product_id
        self.quantity = quantity

    def __repr__(self):
        return '<CartItem %r>' % self.id        
    
class OrderModel(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return{
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'quantity': self.quantity
        }

    def __init__(self, user_id, product_id, quantity):
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity

    def __repr__(self):
        return '<Order %r>' % self.id

class OrderItemModel(db.Model):
    __tablename__ = 'order_item'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return{
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity
        }

    def __init__(self, order_id, product_id, quantity):
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity

    def __repr__(self):
        return '<OrderItem %r>' % self.id  

class ReviewModel(db.Model):
    __tablename__ = 'review'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    def to_dict(self):
        return{
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'rating': self.rating,
            'comment': self.comment
        }

    def __init__(self, user_id, product_id, rating, comment):
        self.user_id = user_id
        self.product_id = product_id
        self.rating = rating
        self.comment = comment  # This can be None if no comment is provided.

    def __repr__(self):
        return '<Review %r>' % self.id          
