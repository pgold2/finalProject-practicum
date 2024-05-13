import requests
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from .models import Team
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  ##means from _init_.py import db
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
    teamsFollowed, teams_name, user_name = getFollowedTeams()


     #THIS API CALL IS FOR STATISTICS
    # # Fetch data for the team statistics from your database or any other source
    url = "https://api-nba-v1.p.rapidapi.com/teams/statistics"
    querystring = {"id":"1","season":"2020"}
    headers = {
         "X-RapidAPI-Key": "37b97f1111msh366b855c4b97860p13932ajsnfe18b5af644a",
         "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
     }
    response = requests.get(url, headers=headers, params=querystring)
    team_stats = response.json()

    # Now you can use the 'team_stats' variable in your template
    return render_template('stats_dashboard.html', team_stats=team_stats, user=current_user, teamsFollowed=teamsFollowed,
                           teams=teams_name)
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


def getFollowedTeams():
    # Make the API request to retrieve data about teams
    url = "https://api-nba-v1.p.rapidapi.com/teams"
    headers = {
        "X-RapidAPI-Key": "37b97f1111msh366b855c4b97860p13932ajsnfe18b5af644a",
        "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # Extract the team names from the response
        teams_data = response.json().get('response', [])
        teams_name = [team.get('name') for team in teams_data]
    else:
        # If the request failed, set teams_name to None
        teams_name = None

        # Retrieve the user's first name
    user_name = current_user.first_name  # Assuming the user's first name is stored in the database
    # Retrieve the list of teams followed by the current user
    teamsFollowed = current_user.teams_followed if current_user.teams_followed else []
    return teamsFollowed, teams_name, user_name

