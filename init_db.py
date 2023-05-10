from app import app, db
from app import User, Post, Category, post_category

with app.app_context():
    db.create_all()

u1 = User(username='Arash', password='123456', role='author')
p1 = Post(title='Welcome ali', desc='Welcome to my post', author=u1)
c1 = Category(name='media')

with app.app_context():
    db.session.add_all([u1, p1,c1])
    db.session.commit()