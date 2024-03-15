#where users could go to the standard routes

from flask import Blueprint

views = Blueprint('views', __name__) #sets up a blueprint for the flask application

@views.route('/')
def home():#runs when the / route is called
    return "<h1> Test</h1>"