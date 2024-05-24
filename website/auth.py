import requests
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from .models import Team
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  ##means from _init_.py import db
from flask_login import login_user, login_required, logout_user, current_user
from flask import session, jsonify
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

    selected_team = session.get('selected_team')
    print('this is the selected team', selected_team) #this is being populated as NONE
    teamStatsID = get_team_id(selected_team) if selected_team else 1
    print('this is the id', teamStatsID) #therefore, this is none as well

     #THIS API CALL IS FOR STATISTICS
    # # Fetch data for the team statistics from your database or any other source
    url = "https://api-nba-v1.p.rapidapi.com/teams/statistics"
    querystring = {"id":teamStatsID, "season":"2023"}
    headers = {
         "X-RapidAPI-Key": "37b97f1111msh366b855c4b97860p13932ajsnfe18b5af644a",
         "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
     }
    response = requests.get(url, headers=headers, params=querystring)
    team_stats = response.json()
    print(team_stats)  # print to console to inspect the data

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
        #print(response.json())

        # Render the template with the data
        teams_data = response.json()['response']

        teams = []
        for team in teams_data:
            #print(team)

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


@auth.route('/set_selected_team', methods=['POST'])
def set_selected_team():
    data = request.json
    session['selected_team'] = data['selected_team']
    return jsonify({"status": "success"})
# @auth.route('/set_selected_team', methods=['POST'])
# def set_selected_team():
#     selected_team = request.json['selected_team']
#     session['selected_team'] = selected_team
#     return jsonify({'result': 'success'}), 200

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

def get_team_id(team_name):
    team_mapping = {
        'Atlanta Hawks': 1,
        'Boston Celtics': 2,
        'Brisbane Bullets': 3,
        'Brooklyn Nets': 4,
        'Charlotte Hornets': 5,
        'Chicago Bulls': 6,
        'Cleveland Cavaliers': 7,
        'Dallas Mavericks': 8,
        'Denver Nuggets': 9,
        'Detroit Pistons': 10,
        'Golden State Warriors': 11,
        'Guangzhou Long-Lions': 12,
        'Haifa Maccabi Haifa': 13,
        'Houston Rockets': 14,
        'Indiana Pacers': 15,
        'LA Clippers': 16,
        'Los Angeles Lakers': 17,
        'Melbourne United': 18,
        'Memphis Grizzlies': 19,
        'Miami Heat': 20,
        'Milwaukee Bucks': 21,
        'Minnesota Timberwolves': 22,
        'New Orleans Pelicans': 23,
        'New York Knicks': 24,
        'Oklahoma City Thunder': 25,
        'Orlando Magic': 26,
        'Philadelphia 76ers': 27,
        'Phoenix Suns': 28,
        'Portland Trail Blazers': 29,
        'Sacramento Kings': 30,
        'San Antonio Spurs': 31,
        'Shanghai Sharks': 32,
        'Sydney Kings': 33,
        'Team Team Durant': 34,
        'Team LeBron': 35,
        'Away Team Wilbon': 36,
        'Home Team Stephen A': 37,
        'Toronto Raptors': 38,
        'USA USA': 39,
        'Utah Jazz': 40,
        'Washington Wizards': 41,
        'World World': 42,
        'Team Africa': 43,
        'Team World': 44,
        'Paschoalotto/Bauru': 83,
        'Fenerbahce Sports Club': 84,
        'Olimpia Milano': 85,
        'Real Madrid Real Madrid': 86,
        'Rio de Janeiro Flamengo': 87,
        'Barcelona FC Barcelona': 88,
        'Buenos Aires San Lorenzo': 89,
        'Adelaide 36ers': 90,
        'Beijing Ducks': 91,
        'New Zealand Breakers': 92,
        'Perth Wildcats': 93,
        'Team USA': 94,
        'Team World': 95,
        'Team China': 96,
        'Team Croatia': 97,
        'Franca Franca': 99
    }
    return team_mapping.get(team_name, "Team not found")

