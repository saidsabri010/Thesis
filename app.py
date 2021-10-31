from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():  # put application's code here
    return render_template('index.html')


@app.route('/login')
def login():  # put application's code here
    return render_template('login.html')


@app.route('/signup')
def signup():  # put application's code here
    return render_template('signup.html')


if __name__ == '__main__':
    app.run()
