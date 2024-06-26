from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_migrate import Migrate #added this to add a teams column

db = SQLAlchemy()
#This is the connection to AWS
#DB_NAME = "database-2"


DB_NAME = "database.db" #for local connection

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'

    # for local connection
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

#This is the connection to AWS
    #app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://admin:playpulse@database-2.czu4sq4uomtn.us-east-1.rds.amazonaws.com/{DB_NAME}'
    db.init_app(app)
    migrate = Migrate(app, db)#added this to add a teams column

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Note
    
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
