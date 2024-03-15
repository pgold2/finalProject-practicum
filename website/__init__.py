# from flask import Flask
# from config import Config
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
#
# app = Flask(__name__)
# app.config.from_object(Config)
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)
#

from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret key'  # encrypts or secures session cookies of the website
    return app
