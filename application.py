#!/usr/bin/env python

"""
This is the main python application for the Exercise Catalog Application.

This application connects to the exercisecatalog PostgreSQL database and
returns information related to various categories of exercises, as well
as the exercises themselves. The user has the ability to login with Google,
using Oauth2, and once logged in, can add, edit, and delete exercises that
they themselves are the owner of. The user can view exercises that they are
not the owner of, but cannot edit or delete.

This application utilizes Python, Flask, and SQLAlchemy and uses Oauth2 for
authentication and authorization.
"""

# Importing Flask
from flask import (
    flash,
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

# Imports for SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import (
    Base,
    Exercises,
    PrimaryCategories,
    SecondaryCategories,
    Users,
)

import re

# Imports for local permissions
from flask import session as login_session
import random
import string

# Imports for Oauth2 implementation
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# Client ID for Google Login
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "Green Machine Exercise Catalog"

# Connecting to PostgreSQL DB exercisecatalog
engine = create_engine('postgresql:///exercisecatalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/exercises/')
def homepage():
    """Render the homepage with primary categories listed."""
    primary_categories = session.query(PrimaryCategories).all()
    return render_template('homepage.html',
                           category_names=primary_categories,
                           first_name=login_name())


@app.route('/exercises/<int:primary_category_id>/')
def show_secondary_categories(primary_category_id):
    """Render the secondary categories on the page.

    Secondary categories are dependent on the primary category selected.
    """
    # Isolates the primary category from the primary category ID.
    primary = (
        session.query(PrimaryCategories)
        .filter_by(id=primary_category_id).one()
    )

    # Selects all secondary categories based on the selecte primary category.
    secondary_categories = (
        session.query(SecondaryCategories)
        .filter(SecondaryCategories.primary_category == primary_category_id)
    )
    return render_template('secondary.html',
                           secondary_category=secondary_categories,
                           primary_category=primary,
                           primary_id=primary.id, first_name=login_name())


@app.route('/exercises/<int:primary_category_id>/<int:secondary_id>/')
def show_exercises_in_category(primary_category_id, secondary_id):
    """Render a page with a list of all exercises.

    Exercises are based on the secondary category.
    Provide an add an exercise button.
    """
    # Isolates the primary category from the primary category ID.
    primary = (
        session.query(PrimaryCategories)
        .filter_by(id=primary_category_id).one()
    )

    # Find the secondary category information based on secondary ID.
    secondary_info = (
        session.query(SecondaryCategories.name, SecondaryCategories.id)
        .filter_by(id=secondary_id).one()
    )

    """Find all exercises tied to the secondary category."""
    exercises = (
        session.query(Exercises)
        .filter(secondary_id == Exercises.secondary_category)
    )

    return render_template('exercises.html',
                           primary_category_id=primary.id,
                           secondary_id=secondary_info.id,
                           exercise_names=exercises,
                           category_name=secondary_info,
                           first_name=login_name())


@app.route('/exercises/<int:primary_category_id>/<int:secondary_id>/'
           '<string:exercise_name>/')
def show_exercise_description(primary_category_id, secondary_id,
                              exercise_name):
    """Display a specific exercise selected.

    Display with exercise name, description, and an embedded YouTube video.
    If the user is the owner, they will be able to edit or delete the exercise.
    If they are not, they can only view the exercise.
    """
    """Reformat the exercise name that was passed in through
    the URL to exclude dashes.
    """
    exercise_name = exercise_name.replace('-', ' ')
    exercise_name = re.sub(r'   ', ' - ', exercise_name)

    # Display primary category.
    primary = (
        session.query(PrimaryCategories)
        .filter_by(id=primary_category_id).one()
    )
    # Display secondary category.
    secondary_info = (
        session.query(SecondaryCategories.id)
        .filter_by(id=secondary_id).one()
    )
    # Display exercise.
    exercise_info = (
        session.query(Exercises).filter_by(name=exercise_name).one()
    )

    # Find the creator of the exercise.
    creator = get_user_info(exercise_info.user_id)

    """If user is not logged in or they are not the creator, take to public
    version of the page without editing and deleting privileges.
    Otherwise, take to private page with editing and deleting privileges.
    """
    if (
        'username' not in login_session or
        creator.id != login_session['user_id']
    ):
        return render_template('publicExerciseDescription.html',
                               primary_category_id=primary.id,
                               secondary_id=secondary_info,
                               exercise=exercise_info, creator=creator)
    else:
        return render_template('exerciseDescription.html',
                               primary_category_id=primary.id,
                               secondary_id=secondary_info,
                               exercise=exercise_info,
                               first_name=login_name(),
                               creator=creator)


@app.route('/exercises/<int:primary_category_id>/<int:secondary_id>/'
           '<string:exercise_name>/edit/', methods=['GET', 'POST'])
def edit_exercise(primary_category_id, secondary_id, exercise_name):
    """Allow user to edit an exercise.

    All fields must be edited, including name, description, and video url.
    All edits are saved to the exercisecatalog DB.
    """
    """Reformatting the name that was passed in through
    the URL to exclude dashes."""
    exercise_name = exercise_name.replace('-', ' ')
    exercise_name = re.sub(r'   ', ' - ', exercise_name)

    # Find specific exercise based on passed in exercise name.
    exercises = session.query(Exercises).filter_by(name=exercise_name).one()

    # If user is not logged in, redirect to the login page.
    if 'username' not in login_session:
        return redirect('/login')

    """If user is not the creator of the exercise, alert them that
    they are not authorized."""
    if exercises.user_id != login_session['user_id']:
        return (
            "<script>function notAuthorized()"
            "{alert('You are not authorized to edit this exercise."
            "'Please create your own exercise in order to edit.')}</script>"
            "<body onload='notAuthorized()'>"
        )
    """Make changes to the database based on edits made. Then redirect to the
    page with the list of exercises."""
    if request.method == 'POST':
        if (
            request.form['name'] or request.form['description'] or
            request.form['video_url']
        ):
            exercises.name = request.form['name']
            exercises.description = request.form['description']
            exercises.video_url = request.form['video_url']
        session.add(exercises)
        session.commit()
        flash("Your exercise has been edited!")
        return redirect(url_for('show_exercises_in_category',
                                primary_category_id=primary_category_id,
                                secondary_id=secondary_id))
    else:
        return render_template('editExercise.html',
                               exercises=exercises,
                               primary_category_id=primary_category_id,
                               secondary_id=secondary_id)


@app.route('/exercises/<int:primary_category_id>/<int:secondary_id>/'
           '<string:exercise_name>/delete/', methods=['GET', 'POST'])
def delete_exercise(primary_category_id, secondary_id, exercise_name):
    """Allow the user to delete all information regarding an exercise.

    The user must be the owner of the exercise to delete.
    """
    """Reformat the name that was passed in through the URL
    to exclude dashes."""
    exercise_name = exercise_name.replace('-', ' ')
    exercise_name = re.sub(r'   ', ' - ', exercise_name)

    # SQLAlchemy query to identify exercise to be deleted.
    to_delete = session.query(Exercises).filter_by(name=exercise_name).one()

    # If user is not logged in, redirect to the login page.
    if 'username' not in login_session:
        return redirect('/login')

    """If user is not the creator of the exercise, alert them that they are
    not authorized."""
    if to_delete.user_id != login_session['user_id']:
        return (
            "<script>function notAuthorized()"
            "{alert('You are not authorized to delete this exercise."
            "'Please create your own exercise in order to delete.')}</script>"
            "<body onload='notAuthorized()'>"
        )

    """Delete exercise from database. Then redirect to list of exercises."""
    if request.method == 'POST':
        session.delete(to_delete)
        session.commit()
        flash("This exercise has been deleted!")
        return redirect(url_for('show_exercises_in_category',
                                primary_category_id=primary_category_id,
                                secondary_id=secondary_id))
    else:
        return render_template('deleteExercise.html',
                               exercise_name=exercise_name,
                               primary_category_id=primary_category_id,
                               secondary_id=secondary_id)


@app.route('/exercises/<int:primary_category_id>/<int:secondary_id>/add/',
           methods=['GET', 'POST'])
def add_exercise(primary_category_id, secondary_id):
    """Allow the user to add an exercise to the database.

    All fields are required, including the name, description, and YouTube video
    embed URL. Any user may add an exercise, but the user must be logged in.
    """
    # SQLAlchemy query to identify secondary category to store new exercise in.
    name = session.query(SecondaryCategories).filter_by(id=secondary_id).one()

    # If user is not logged in, redirect to the login page.
    if 'username' not in login_session:
        return redirect('/login')

    """Add exercise to the database. Then redirect to list of exercises."""
    if request.method == 'POST':
        new_exercise = (
            Exercises(name=request.form['name'],
                      description=request.form['description'],
                      video_url=request.form['video_url'],
                      secondary_category=secondary_id,
                      user_id=login_session['user_id'])
        )

        session.add(new_exercise)
        session.commit()
        flash("Your new exercise has been created!")
        return redirect(url_for('show_exercises_in_category',
                                primary_category_id=primary_category_id,
                                secondary_id=secondary_id))
    else:
        return render_template('addExercise.html',
                               category_name=name,
                               primary_category_id=primary_category_id,
                               secondary_id=secondary_id)


@app.route('/login')
def login():
    """Render the login page, which prompts users to login with Google."""
    # Storing state token information.
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Allow a user to login with their Google account using Oauth2.

    Once logged in, information about the user is stored, such as their
    username, picture, email, and first name.
    """
    # If state token does not match user's state token, alert user.
    if request.args.get('state') != login_session['state']:
        r_json = 'Invalid state token.'
        error_code = 401
        r = 'Sorry, we cannot log you in.'
        gconnect_errors(r_json, error_code, r)

    code = request.data

    try:
        """Upgrade the authorization code into a credentials object.
        If there is an error, alert user."""
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        r_json = 'Failed to upgrade the authorization code.'
        error_code = 401
        r = 'Sorry, we cannot log you in.'
        gconnect_errors(r_json, error_code, r)

    # Check to see if the access token is valid.
    access_token = credentials.access_token
    url = (
           'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token
    )
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    """If there is an error in the access token info,
    then do not log in and return an error."""
    if result.get('error') is not None:
        print "ERROR ERROR"
        r_json = 'error'
        error_code = 500
        r = 'Sorry, we cannot log you in.'
        gconnect_errors(r_json, error_code, r)

    """Verify that access token is for the intended user.
    Otherwise, return an error."""
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        r_json = "Token's user ID does not match given user ID."
        error_code = 401
        r = 'Sorry, we cannot log you in.'
        gconnect_errors(r_json, error_code, r)

    """Verify that the access token is valid for the app.
    Otherwise, return an error."""
    if result['issued_to'] != CLIENT_ID:
        r_json = "Token's client ID does not match app's"
        error_code = 401
        r = 'Sorry, we cannot log you in.'
        gconnect_errors(r_json, error_code, r)

    """Check to see if the user is already logged into the system.
    If so, alert user."""
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        r_json = 'Current user is already logged in.'
        error_code = 200
        r = 'You are already signed in.'
        gconnect_errors(r_json, error_code, r)

    # Store access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info.
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    # Storing user information.
    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]
    login_session['first_name'] = data["given_name"]

    # If user does not exist, create a new user.
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    # Flash Login message to user and render the login confirmation page.
    flash("You are now logged in as %s" % login_session['username'])
    return render_template('gconnect.html',
                           first_name=login_session['first_name'],
                           picture=login_session['picture'])


def gconnect_errors(r_json, error_code, r):
    """Return a response if an error occurs when signing in with Google."""
    response = make_response(json.dumps(r_json), error_code)
    response.headers['Content-Type'] = 'application/json'
    return render_template('gdisconnect.html',
                           thanks='',
                           response=r)


@app.route("/gdisconnect")
def gdisconnect():
    """Disconnect an already connected Google user from the application."""
    # Checking to see if user is connected. If they are not, alert the user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps
                                 ('Current user is not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return render_template('gdisconnect.html',
                               thanks='',
                               response='Sorry, you are not currently'
                               'signed in.')

    # Execute HTTP GET request to revoke current token.
    url = (
           'https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token']
    )
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Resetting the user's session
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['first_name']

        # Confirm to user that they have been logged out.
        response = make_response(json.dumps('Sign out is successful.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return render_template('gdisconnect.html',
                               thanks='Thank you for stopping by!',
                               response='You have succesfully signed out.'
                               ' Please come again!')

    else:
        # Alert user that there was in an error in logging out.
        response = make_response(json.dumps('Cannot disconnect.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return render_template('gdisconnect.html',
                               thanks='',
                               response='Sorry, we could not disconnect you.'
                               ' Please try again.')


@app.route('/exercises/<int:primary_category_id>/<int:secondary_id>/JSON/')
def exercises_JSON(primary_category_id, secondary_id):
    """Create an API Endpoint for exercises within a secondary category."""
    exercises = (
        session.query(Exercises)
        .filter_by(secondary_category=secondary_id).all()
    )
    return jsonify(Exercises=[i.serialize for i in exercises])


@app.route('/exercises/<int:primary_category_id>/JSON/')
def secondary_categories_JSON(primary_category_id):
    """Create an API Endpoint for all secondary categories."""
    categories = (
        session.query(SecondaryCategories)
        .filter_by(primary_category=primary_category_id).all()
    )
    return jsonify(Categories=[i.serialize for i in categories])


@app.route('/exercises/JSON/')
def primary_categories_JSON():
    """Create an API Endpoint for all primary categories."""
    categories = session.query(PrimaryCategories).all()
    return jsonify(Categories=[i.serialize for i in categories])


def login_name():
    """Display first name on the page when user is logged in."""
    if 'username' in login_session:
        first_name = login_session['first_name']
        return first_name
    else:
        first_name = ''
        return first_name


def get_user_id(email):
    """Find the user ID based on email for local permissions."""
    try:
        user = session.query(Users).filter_by(email=email).one()
        return user.id
    except:
        return None


def get_user_info(user_id):
    """Return all user information based on user ID."""
    user = session.query(Users).filter_by(id=user_id).one()
    return user


def create_user(login_session):
    """Create a new user if user does not yet exist."""
    new_user = (
        Users(name=login_session['username'],
              email=login_session['email'],
              picture=login_session['picture'])
    )

    session.add(new_user)
    session.commit()
    user = session.query(Users).filter_by(email=login_session['email']).one()
    return user.id


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
