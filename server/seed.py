from faker import Faker
from app import app
from models import db, UserModel, ProductModel, cartModel, cartItemModel, OrderModel, OrderItemModel, ReviewModel

fake = Faker()

with app.app_context():
    db.drop_all()
    db.create_all()

    for _ in range(100):
        name = fake.name()
        email = fake.email()
        password = fake.password()

        user = UserModel(username=name, email=email, password=password)
        db.session.add(user)

        product = ProductModel(name=name, price=10.00, stock=100)
        db.session.add(product)

        # Commit to ensure IDs are generated
        db.session.commit()

        cart = cartModel(user_id=user.id, product_id=product.id, quantity=1)
        db.session.add(cart)
        db.session.commit()

        cart_item = cartItemModel(cart_id=cart.id, product_id=product.id, quantity=1)
        db.session.add(cart_item)

        order = OrderModel(user_id=user.id, product_id=product.id, quantity=1)
        db.session.add(order)
        db.session.commit()
         
         #commit to generate order id
        db.session.commit()

        order_item = OrderItemModel(order_id=order.id, product_id=product.id, quantity=1)
        db.session.add(order_item)

        review = ReviewModel(user_id=user.id, product_id=product.id, rating=5, comment="Great product!")
        db.session.add(review)

        # Commit again after adding the cart, cart_item, order, and order_item
        db.session.commit()
