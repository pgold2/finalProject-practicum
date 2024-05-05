from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from website import db
from sqlalchemy.orm import relationship  # Import the relationship function


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    teamsFollowed = db.Column(db.String(255))  # Add this line for the new column
    teams_followed = relationship('Team', backref='followers')
    notes = db.relationship('Note')


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Add this line to link the team to a user
