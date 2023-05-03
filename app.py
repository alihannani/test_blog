from flask import Flask, render_template, url_for, request , redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from flask_login import  LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length
from flask_bcrypt import Bcrypt



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisismysecretkey'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

with app.app_context():
    db = SQLAlchemy(app)
    bcrypt=Bcrypt(app)
#--------------------------------------------------------------------------------------------------------
class Userd(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)],
                           render_kw={'placeholder': 'username...'})
    password = PasswordField(validators=[InputRequired(), Length(min=6, max=20)],
                           render_kw={'placeholder': 'password...'})
    submit = SubmitField('Create Account')

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)],
                           render_kw={'placeholder': 'Enater Username'})
    password = PasswordField(validators=[InputRequired(), Length(min=6, max=20)],
                           render_kw={'placeholder': 'Enater Password'})
    submit = SubmitField('Login')

#-----------------------------------------------------------------------------------------


post_category = db.Table('post_category', 
                        db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
                        db.Column('category_id', db.Integer, db.ForeignKey('category.id')))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    image = db.Column(db.String(200), nullable=True)
    desc = db.Column(db.String(1000), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    id_labeled = db.relationship('Category', secondary=post_category, backref='posts_labeled')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(30), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    posts = db.relationship('Post', backref='author')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
#-----------------------------------------------------------
@login_manager.user_loader
def load_user(userd_id):
    return User.query.get(int(userd_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Userd.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return render_template('dashboard.html')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = Userd(username=form.username.data, password=hashed_password)
        # existing = db.query.filter_by(username=form.username.data).first()
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)
