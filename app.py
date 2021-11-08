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


@app.route('/login1', methods=['GET', 'POST'])
def login1():  # put application's code here
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('this username does not exist !')
        return render_template("login.html")
    elif password != user.password:
        flash('password is wrong, please try again  !')
        return render_template("login.html")
    login_user(user)
    return redirect(url_for('main'))


@app.route('/signup')
def signup():  # put application's code here
    return render_template('signup.html')


@app.route('/register', methods=['GET', 'POST'])
def register():  # put application's code here
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    password_confirm = request.form['confirm_password']
    user = User.query.filter_by(email=email, username=username).first()
    if user:
        flash("email is already used !")
        return render_template('signup.html')
    elif password != password_confirm:
        flash('password must match')
    else:
        new_user = User(username, email, password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("signup.html")


@app.route('/main')
@login_required
def main():  # put application's code here
    return render_template('main.html')


if __name__ == '__main__':
    db.create_all()
    app.run()
