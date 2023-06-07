from app import app, db
from app import User, Post, Category, post_category
from faker import Faker
import random

fake = Faker()
fakeRoles= ["admin","author","editor"]
fakeCategories = ["war", "government", "politics", "education", "health", "the environment", "economy", "business" ]

with app.app_context():
    db.drop_all()
    db.create_all()

superAdmin = User(username='alireza', password='123456', role='superAdmin')

users = []
categories = []
posts = []
post_categories = []

for i in range(10):
    user = User(username= fake.name(), password=fake.password(), role=random.choice(fakeRoles))
    users.append(user)

for category in fakeCategories:
    categories.append(Category(name=category))

for i in range(100):
    posts.append(Post(title=fake.sentence(), desc=fake.text(), author=random.choice(users)))


with app.app_context():
    db.session.add_all(categories)
    db.session.add_all(users)
    db.session.add_all(posts)

    db.session.commit()