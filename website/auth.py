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
    # Fetch data for the team statistics from your database or any other source
    team_name = "Example Team"  # Replace with actual team name
    total_games_played = 10  # Replace with actual total games played
    total_wins = 6  # Replace with actual total wins
    total_losses = 4  # Replace with actual total losses
    winning_percentage = (
                                 total_wins / total_games_played) * 100 if total_games_played > 0 else 0  # Calculate winning percentage
    average_runs_scored = 4.8  # Replace with actual average runs scored per game
    average_runs_allowed = 3.2  # Replace with actual average runs allowed per game

    # Example game statistics data
    game_statistics = [
        {"date": "2024-04-01", "opponent": "Opponent Team A", "result": "Win", "score": "7-4", "runs_scored": 7,
         "runs_allowed": 4},
        {"date": "2024-04-02", "opponent": "Opponent Team B", "result": "Loss", "score": "2-5", "runs_scored": 2,
         "runs_allowed": 5}
    ]

    return render_template('stats_dashboard.html',
                           team_name=team_name,
                           total_games_played=total_games_played,
                           total_wins=total_wins,
                           total_losses=total_losses,
                           winning_percentage=winning_percentage,
                           game_statistics=game_statistics,
                           user=current_user)


@auth.route('/select_team', methods=['GET', 'POST'])
@login_required
def select_team():
    if request.method == 'POST':
        team_id = request.form.get('team_id')
        # Update the user's selected team
        current_user.selected_team_id = team_id
        db.session.commit()
        return redirect(url_for('stats_dashboard'))  # Redirect to the stats dashboard or wherever you want

    teams = Team.query.all()
    return render_template('select_team.html', teams=teams)
