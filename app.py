import pandas as pd
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_login import login_user, logout_user, login_required, LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'postgresql://ppfbseibxpyhis:c6eeb144316b3ac0b3b03b6de8b3838b108eec7535f34a11445cb5969499c101@ec2-54-74-102-48.eu-west-1.compute.amazonaws.com:5432/d8t7o4cqmc589d'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret-key'
db = SQLAlchemy(app)
db.app = app
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


class Movie(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fmovie = db.Column(db.String(255), nullable=False)
    smovie = db.Column(db.String(255), nullable=False)
    similar = db.Column(db.String(255), nullable=False)

    def __init__(self, fmovie, smovie, similar):
        self.fmovie = fmovie
        self.smovie = smovie
        self.similar = similar


class Title(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)

    def __init__(self, title):
        self.title = title


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
    user = User.query.filter_by(email=email).first()
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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/content', methods=['GET', 'POST'])
@login_required
def content():
    query = db.session.query(Title.title).limit(120)
    return render_template('content.html', examples=query)


df = pd.read_csv('https://raw.githubusercontent.com/saidsabri010/dataset/main/movie_dataset.csv')


def combine_columns(row):
    return row["keywords"] + " " + row["cast"] + " " + row["genres"] + " " + row["director"]


def combine_features(row):
    return row["original_title"] + " " + row["cast"] + " " + row["genres"] + " " + row["director"]


def get_title_from_index(index):
    return df[df.index == index]["title"].values[0]


def get_index_from_title(title):
    return df[df.title == title]["index"].values[0]


@app.route('/recommend', methods=['GET', 'POST'])
@login_required
def recommend():
    query = db.session.query(Title.title).limit(120)
    movie_user_likes = request.form['movie_user_likes']
    second_movie_user_likes = request.form['second_movie_user_likes']
    if df['title'].str.contains(movie_user_likes, second_movie_user_likes).any():
        columns = ['keywords', 'cast', 'genres', 'director', 'original_title']
        for column in columns:
            df[column] = df[column].fillna('')
        df["combined_features"] = df.apply(combine_columns, axis=1)
        df["combined_columns"] = df.apply(combine_features, axis=1)
        vectorizer = CountVectorizer()
        matrix = vectorizer.fit_transform(df["combined_features"])
        matrix2 = vectorizer.fit_transform(df['combined_columns'])
        cosine_sim = cosine_similarity(matrix)
        cosine_sim2 = cosine_similarity(matrix2)
        movie_index = get_index_from_title(movie_user_likes)
        movie_index2 = get_index_from_title(second_movie_user_likes)
        similar_movies = list(enumerate(cosine_sim[movie_index]))
        similar_movies2 = list(enumerate(cosine_sim2[movie_index2]))
        sorted_similar_movies = sorted(similar_movies, key=lambda x: x[1], reverse=True)
        sorted_similar_movies2 = sorted(similar_movies2, key=lambda x: x[1], reverse=True)
        count = 0
        movies = []
        for movie, movie2 in zip(sorted_similar_movies, sorted_similar_movies2):
            if sorted_similar_movies[movie[0]] >= sorted_similar_movies2[movie2[0]]:
                movies.append(get_title_from_index(movie[0]))
                print('this movie of first choice', movie[0])
                data = Movie(movie_user_likes, second_movie_user_likes, get_title_from_index(movie[0]))
                db.session.add(data)
                db.session.commit()
            else:
                movies.append(get_title_from_index(movie2[0]))
                print('this movie is of second choice', movie2[0])
                data = Movie(movie_user_likes, second_movie_user_likes, get_title_from_index(movie2[0]))
                db.session.add(data)
                db.session.commit()
            count += 1
            if count >= 10:
                break
        return render_template('content.html', data=movies, movie1=movie_user_likes, examples=query)
    else:
        flash('this movie does not exist !')
    return redirect(url_for('content'))


if __name__ == '__main__':
    app.run()
