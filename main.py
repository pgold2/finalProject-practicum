from flask import render_template
from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    user = {'username': 'Miguel'}
    return render_template('index.html', title = 'Home', user = user)