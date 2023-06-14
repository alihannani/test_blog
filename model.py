from app import app, db
from app import User, Post, Category, post_category

with app.app_context():
    db.create_all()

u1 = post_category(post_id='1', category_id='1')


with app.app_context():
    db.session.add_all([u1])
    db.session.commit()