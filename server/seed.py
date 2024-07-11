from faker import Faker

from app import app
from models import db, User, Product

fake = Faker()

with app.app_context():
    db.drop_all()
    db.create_all()

    for _ in range(100):
        name = fake.name()
        email = fake.email()
        password = fake.password()

        user = User(username=name, email=email, password=password)
        db.session.add(user)

        product = Product(name=name, price=10.00)
        db.session.add(product)

    db.session.commit()