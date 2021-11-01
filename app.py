from flask_migrate import Migrate
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, logout_user, login_required
from flask_login import LoginManager, UserMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:said@localhost:5432/recommendation'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret-key'
db = SQLAlchemy(app)
db.app = app
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(11), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(15), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():  # put application's code here
    return render_template('index.html')


@app.route('/login')
def login():  # put application's code here
    return render_template('login.html')


@app.route('/login1')
def login1():  # put application's code here
    return render_template('login.html')


@app.route('/signup')
def signup():  # put application's code here
    return render_template('signup.html')


@app.route('/main')
def main():  # put application's code here
    return render_template('main.html')


if __name__ == '__main__':
    db.create_all()
    app.run()
