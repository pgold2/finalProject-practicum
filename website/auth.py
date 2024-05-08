import requests
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from .models import Team
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        teamsFollowed = request.form.get('teamsFollowed')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1),
                            teamsFollowed=teamsFollowed)  # Store teams followed in the database
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)


@auth.route('/StatsDashboard', methods=['GET', 'POST'])
def stats_dashboard():
    # First, make a request to the endpoint that lists all teams
    url = "https://api-nba-v1.p.rapidapi.com/teams"
    headers = {
        "X-RapidAPI-Key": "37b97f1111msh366b855c4b97860p13932ajsnfe18b5af644a",
        "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        teams = response.json()['response']
        # Loop through the user's followed teams and get the name of each team
        team_id = None  # Initialize team_id to None
        for followed_team in current_user.teamsFollowed:
            team_name = followed_team
            print(f"Followed team name: {team_name}")  # Print the followed team name
            for team in teams:
                if team['name'] == team_name:
                    team_id = team['id']
                    print(f"Matched team ID: {team_id}")  # Print the matched team ID
                    break

    # Check if team_id is still None
    if team_id is None:
        # Handle case where team name from user's followed teams did not match any team name in API response
        # For example, you can return an error message
        flash('Team not found.', category='error')
        return redirect(url_for('views.home'))

    # Then, make a request to the statistics endpoint using the team's ID
    url = "https://api-nba-v1.p.rapidapi.com/teams/statistics"
    querystring = {"id": team_id, "season": "2023"}

    response = requests.get(url, headers=headers, params=querystring)
    team_stats = response.json()

    print(team_stats)

    teamsFollowed = current_user.teams_followed if current_user.teams_followed else []

    return render_template('stats_dashboard.html', team_stats=team_stats, user=current_user, teamsFollowed=teamsFollowed)
# @auth.route('/select_team', methods=['GET', 'POST'])
# @login_required
# def select_team():
#     if request.method == 'POST':
#         team_id = request.form.get('team_id')
#         # Update the user's selected team
#         current_user.selected_team_id = team_id
#         db.session.commit()
#         return redirect(url_for('stats_dashboard'))  # Redirect to the stats dashboard or wherever you want
#
#     teams = Team.query.all()
#     return render_template('select_team.html', teams=teams)
#

@auth.route('/add_team', methods=['GET', 'POST'])
@login_required
def add_team():
    # Make the API request to retrieve data about teams
    url = "https://api-nba-v1.p.rapidapi.com/teams"
    headers = {
        "X-RapidAPI-Key": "37b97f1111msh366b855c4b97860p13932ajsnfe18b5af644a",
        "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Print the response to inspect its structure
        print(response.json())

        # Render the template with the data
        teams_data = response.json()['response']

        teams = []
        for team in teams_data:
            print(team)

            team_name = team['name']

            teams.append(team_name)

    if request.method == 'POST':
        team_name = request.form.get('team')

        # Create a new Team object with the specified name
        new_team = Team(name=team_name)

        # Add the new Team object to the database
        db.session.add(new_team)

        # Add the new Team object to the teams_followed list of the current_user
        current_user.teams_followed.append(new_team)

        # Commit the changes to the database
        db.session.commit()

        flash('Team added successfully!', category='success')
        return redirect(url_for('views.home'))

    return render_template('add_team.html', teams=teams, user=current_user)
