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

    if request.method == 'POST':
        note = request.form.get('note')  # Gets the note from the HTML

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)  # Create a new Note object
            db.session.add(new_note)  # Add the new Note object to the database
            db.session.commit()  # Commit the changes to the database
            flash('Note added!', category='success')

    # Render the home.html template with the retrieved data
    return render_template('home.html', user=current_user, user_name=user_name,
                           teamsFollowed=teamsFollowed, teams=teams_name)


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
    # model named Team to represent teams
    teams = Team.query.all()  # Retrieve all teams from the database

    if request.method == 'POST':
        # Assuming the form sends the selected team's ID
        team_id = request.form.get('team_id')
        # Logic to handle the selected team, such as updating the user's selected team
        # You can update the current user's selected team in the database here
        flash('Team selection updated!', category='success')

    return render_template('select_team.html', teams=teams)


#@views.route('/update_teams_followed', methods=['POST'])
#@login_required
#def update_teams_followed():
#    teams_followed = request.form.getlist('teams_followed')  # Assuming you're using checkboxes to select teams
#    current_user.teamsFollowed = ','.join(teams_followed)  # Convert list to comma-separated string
#    db.session.commit()
#   flash('Teams followed updated successfully!', category='success')
#   return redirect(url_for('views.select_team'))

