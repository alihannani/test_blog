from flask import Flask, render_template,jsonify, url_for, request , redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from flask_login import  LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,FileField
from wtforms.validators import InputRequired, Length
from wtforms.widgets import TextArea
from flask_bcrypt import Bcrypt
import os

#-------------------------------------------------------------------------------------------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisismysecretkey'
app.config['UPLOAD_FOLDER']= 'static/pictures'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

with app.app_context():
    db = SQLAlchemy(app)
    bcrypt=Bcrypt(app)
#--------------------------------------------------------------------------------------------------------





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

class PostForm(FlaskForm):
    title= StringField(validators=[InputRequired()])
    tags= StringField(validators=[InputRequired()])
    content= StringField(validators=[InputRequired()],widget=TextArea())
    picture = FileField()
    submit=SubmitField('Creat post')


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
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
                
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password, role='author')
        # existing = db.query.filter_by(username=form.username.data).first()
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    #if current_user.role == 'admin':#
    posts = Post.query.filter_by(author_id=current_user.id)
    return render_template('dashboard.html', current_user=current_user,posts=posts)
@app.route('/by/<name>')
def written_by(name):
    posts = Post.query.filter_by(author_id=name)
    return render_template('index.html', posts=posts)





@app.route('/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        picture= form.picture.data
        if picture:
            filename=str(Post.query.count()+1)+picture.filename.split('0')[0]+'.'+picture.filename.split('.')[-1]
            filedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], filename)
            picture.save(filedir)
            post = Post(title=form.title.data,
                    desc=form.content.data,
                    image=filename)
        
            tags = form.tags.data.split(',')
        else:
            post = Post(title=form.title.data,
                        desc=form.content.data)
        tags = form.tags.data.split(',')
        for tag in tags:
            tag_in_db = Category.query.filter_by(name=tag).first()
            if not tag_in_db:
                tag_in_db=Category(name=tag)
            post.id_labeled.append(tag_in_db)
            db.session.add(tag_in_db)
            db.session.commit()
        post.author = current_user
        form.title.data =''
        form.tags.data =''
        form.content.data =''
        db.session.add(post)
        db.session.commit()
        
    return render_template('new_post.html', form=form)
@app.route('/search/<text>')
def search(text):
    
    all_posts = Post.query.all()
    posts = []
    for post in all_posts :
        if text in post.desc:
            posts.append(post)
        elif text in post.title:
            posts.append(post)
    return render_template('dashboard.html', posts=posts, user=current_user)
   
#------------------------------------------------------------------------------
@app.route('/delete/<int:id>')
def delete(id):
    post = Post.query.get_or_404(id)
    try:
        db.session.delete(post)
        db.session.commit()
        return redirect('/dashboard')   
    except:
        return 'there was a problem dejeting the task'
@app.route('/update/<int:id>', methods=['POST', 'GET'])
def update(id):
    post = Post.query.get_or_404(id)
    if request.method == 'GET':
        return render_template('update.html', post=post)
    elif request.method == 'POST':
        post.desc = request.form['content']
        db.session.add(post)
        db.session.commit()
        return redirect('/dashboard')


@app.route('/api/all')
def get_all():
    posts = Post.query.all()
    response = []
    for post in posts:
        current_post = {'title': post.title,
                'author': post.author.username,
                'text': post.desc}
        response.append(current_post)
    return jsonify(response)
@app.route('/tag/<name>')
def posts_tagged(name):
    tag = Category.query.filter_by(name=name).first()
    posts = tag.posts_labeled
    return render_template('index.html',posts=posts, user=current_user)
#---------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True,port=7000)

