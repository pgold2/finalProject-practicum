from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from flask import request
from .models import Note, Team
from . import db
import json
import requests

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    # Make the API request to retrieve data about teams
    url = "https://api-nba-v1.p.rapidapi.com/teams"
    headers = {
        "X-RapidAPI-Key": "37b97f1111msh366b855c4b97860p13932ajsnfe18b5af644a",
        "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Render the template with the data
        teams_name = response.json()['response']
    else:
        # If the request failed, return an error message
        teams_name = None

    # added this to display user's name and team
    user_name = current_user.first_name  # Assuming the user's first name is stored in the database
    teamsFollowed = current_user.teamsFollowed  # Assuming teams followed are stored in the database
    if teamsFollowed is None:
        teamsFollowed = []  # Handle case where teamsFollowed is None

    if request.method == 'POST':
        note = request.form.get('note')  # Gets the note from the HTML

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)  # providing the schema for the note
            db.session.add(new_note)  # adding the note to the database
            db.session.commit()
            flash('Note added!', category='success')

    return render_template('home.html', user=current_user, user_name=user_name, teamsFollowed=teamsFollowed,
                           teams=teams_name)


# return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)  # this function expects a JSON from the INDEX.js file
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


@views.route('/select_team', methods=['GET', 'POST'])
@login_required
def select_team():
    # Fetch teams available for selection
    # Assuming you have a model named Team to represent teams
    teams = Team.query.all()  # Retrieve all teams from the database

    if request.method == 'POST':
        # Assuming the form sends the selected team's ID
        team_id = request.form.get('team_id')
        # Logic to handle the selected team, such as updating the user's selected team
        # You can update the current user's selected team in the database here
        flash('Team selection updated!', category='success')

    return render_template('select_team.html', teams=teams)


@views.route('/update_teams_followed', methods=['POST'])
@login_required
def update_teams_followed():
    teams_followed = request.form.getlist('teams_followed')  # Assuming you're using checkboxes to select teams
    current_user.teamsFollowed = ','.join(teams_followed)  # Convert list to comma-separated string
    db.session.commit()
    flash('Teams followed updated successfully!', category='success')
    return redirect(url_for('views.select_team'))


