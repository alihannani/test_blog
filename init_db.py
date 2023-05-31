from app import app, db
from app import User, Post, Category, post_category

with app.app_context():
    db.create_all()

