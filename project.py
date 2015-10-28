from flask import Flask, render_template, request, redirect, jsonify, \
    url_for, flash
from flask import session as login_session
from flask.ext.seasurf import SeaSurf

from sqlalchemy import create_engine, asc, desc, \
    func, distinct
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.serializer import loads, dumps
from database_setup import Base, City, Event, User
import random
import string
import logging
import json
import httplib2
import requests

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response

from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from datetime import datetime


app = Flask(__name__)
# Use SeaSurf to prevent cross-site request forgery
csrf = SeaSurf(app)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Android Events"


# Connect to database and create database session
engine = create_engine('sqlite:///androidevents.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state: %s" % login_session['state'] #Debug
    return render_template('login.html', STATE=state)


# Login using Facebook credentials and CSRF
@csrf.exempt
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.5/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # Check if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("Now logged in as %s" % login_session['username'])
    return output


# Logout from Facebook credentials
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    del login_session['facebook_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['provider']

    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# Login with Google Plus credentials and CSRF 
@csrf.exempt
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        print "FlowExchangeError"
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
        print "UserId does not match GPlusId"
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # Check if user exists, if not create a new user
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Logout from Google Plus credentials
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        # Display page listing all cities
        return redirect(url_for('showCities'))
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        # Display page listing all cities
        return redirect(url_for('showCities'))
    else:
        # For whatever reason, the given token was invalid
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Android Event information
# Return all events for one city
@app.route('/city/<int:city_id>/event/JSON')
def cityEventsJSON(city_id):
    city = session.query(City).filter_by(id=city_id).one()
    events = session.query(Event).filter_by(
        city_id=city_id).all()
    events_to_serialize = [e.serialize for e in events]
    return jsonify(cityEvents=[city.serialize])


# Return all cities and all events
@app.route('/all-events/JSON')
def allCitiesAndEventsJSON():
    # Query to get data of interest
    city = session.query(City).all()
    return jsonify(allEvents=[c.serialize for c in city])


# XML APIs to view Android Event information
@app.route('/all-events/XML')
def allCitiesAndEventsXML():
    # Query to get data of interest
    city = session.query(City).all()

    # Declare root node of XML
    top = Element('allEvents')
    comment = Comment('XML Response with all cities and events')
    top.append(comment)

    # Loop through query responses and format as XML 
    for c in city:
        event = SubElement(top, 'event')
        child = SubElement(event, 'id')
        child.text = str(c.id)
        child = SubElement(event, 'city')
        child.text = c.name
        child = SubElement(event, 'state')
        child.text = c.state
        eventInfo = SubElement(event, 'eventInfo')  # Add new node for Events
        for e in c.events:
            en = SubElement(eventInfo, 'event_name')
            en.text = e.name
            child = SubElement(en, 'description')
            child.text = e.description
            child = SubElement(en, 'event_date')
            child.text = str(e.event_date)
            child = SubElement(en, 'event_url')
            child.text = e.event_url
            child = SubElement(en, 'user_id')
            child.text = str(e.user_id)
     
        print tostring(top)
    return app.response_class(tostring(top), mimetype='application/xml')


# Display all cities 
@app.route('/')
@app.route('/city/')
def showCities():
    # List all cities (data for left-hand card panel)
    cities = session.query(City).order_by(asc(City.name))

    # List all events (data for right-hand card panel)
    allEvents = session.query(Event).join(Event.city).\
                order_by(Event.event_date.desc(), City.name, Event.name).all()
    
 
    # Subquery to get count of events in each city
    q = session.query(City.id).subquery()
    cityCountTest = session.query(City.id, City.name, func.count(Event.city_id)).\
        filter(Event.city_id.in_(q)).\
        join(Event.city).\
        group_by(City.name)      
    
    
    cityCountTest1 = session.query(City.name, func.count(Event.city_id)).\
                    filter(Event.city_id ==\
                    session.query(City.id).\
                    join(Event.city)).\
                    group_by(City.name)

    theCityId = session.query(City.id).subquery('cid')

    test = session.query(City).join(Event.city)

    # Returns total num of cities
    cityCount = session.query(func.count(City.id)).scalar()
    app.logger.info(cityCount)

    # Test query
    for eventCountByCity in session.query(func.count(Event.city_id)).\
        filter(Event.city_id == '5'):
        app.logger.info(eventCountByCity)

    return render_template('cities.html', cities=cities, allEvents=allEvents)


# Add a new City
@app.route('/city/new/', methods=['GET', 'POST'])
def newCity():
    # Only logged in users can add data
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        newCity = City(name=request.form['city'], state=request.form['state'], 
            user_id = login_session['user_id'])
        session.add(newCity)
        flash('New City "%s" Successfully Created' % newCity.name)
        session.commit()
        return redirect(url_for('showCities'))
    else:
        return render_template('newCity.html')


# Edit a City
@app.route('/city/<int:city_id>/edit/', methods=['GET', 'POST'])
def editCity(city_id):
    editedCity = session.query(City).filter_by(id=city_id).one()
    # Only logged in users can edit a city
    if 'username' not in login_session:
        return redirect('/login')
    # Only user that submitted city can edit the city information
    if editedCity.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not \
                authorized to edit this city.');}</script><body \
                onload='myFunction()''>"
    # Submit edits of city data
    if request.method == 'POST':
        app.logger.info('POST request called')
        if request.form['name']:
            editedCity.name = request.form['name']
        if request.form['state']:
            editedCity.state = request.form['state']
            flash('City Successfully Edited %s' % editedCity.name)
            return redirect(url_for('showCities'))
    else:
      return render_template('editCity.html', city=editedCity)


# Delete a city
@app.route('/city/<int:city_id>/delete/', methods=['GET', 'POST'])
def deleteCity(city_id):
    cityToDelete = session.query(City).filter_by(id=city_id).one()
    # Only logged in users can delete a city
    if 'username' not in login_session:
        return redirect('/login')
    # Only user that submitted city can delete the city information
    if cityToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not \
                authorized to delete this city.');}</script><body \
                onload='myFunction()''>"
    # Submit request to delete city
    if request.method == 'POST':
        session.delete(cityToDelete)
        flash('%s Successfully Deleted' % cityToDelete.name)
        session.commit()
        return redirect(url_for('showCities', city_id=city_id))
    else:
        return render_template('deleteCity.html', cityToDelete=cityToDelete)


# Show all events in all cities (available from navigation menu)
@app.route('/all-events/')
def showAllEvents():
    allEvents = session.query(Event).join(Event.city).\
    order_by(Event.event_date.desc(), City.name, Event.name).all()
    return render_template('all-events.html', allEvents=allEvents)


# Show all events in selected city
@app.route('/city/<int:city_id>/')
@app.route('/city/<int:city_id>/event/')
def showEvent(city_id):
    # List all cities (data for left-hand card panel)
    cities = session.query(City).order_by(asc(City.name))

    # Filter display in right-hand panel to events in selected city
    city = session.query(City).filter_by(id=city_id).one() 
    
    # Get all events in selected city
    events = session.query(Event).filter_by(city_id=city_id).\
            order_by(desc(Event.event_date)).all()
    
    # Get count of events in selected city
    eventCountByCity = session.query(func.count(Event.city_id)).\
                        filter(Event.city_id == city_id).\
                        scalar()
    return render_template('event.html', cities=cities, city=city, 
        eventCountByCity=eventCountByCity, events=events)


# Show event details  
@app.route('/city/<int:city_id>/event-details/<int:event_id>')
def showEventDetails(city_id, event_id):
    # Filter display on right-hand panel to events in selected city
    city = session.query(City).filter_by(id=city_id).one() 
    # Get all events in selected city
    event = session.query(Event).filter_by(id=event_id).one()
    return render_template('eventDetails.html', city=city, event=event)


# Create a new event in a city 
@app.route('/event/new/', methods=['GET', 'POST'])
def newEvent():
    # Query all city locations to populate select menu in form
    locations = session.query(City).all()
    # Only logged in users can add data 
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        # Format date value before submitting to database
        dt = request.form['event_date']
        dt_obj = datetime.strptime(dt, '%Y-%m-%d')
        
        # Create event object based on form data
        newEvent = Event(name=request.form['event'], 
            description=request.form['description'], 
            event_date=dt_obj, event_url=request.form['event_url'], 
            image_url=request.form['image_url'], 
            city_id=request.form['city_id'], user_id=login_session['user_id'])
        session.add(newEvent)
        session.commit()
        flash('New Event "%s" Successfully Created' % (newEvent.name))
        return redirect(url_for('showEvent', city_id=newEvent.city_id))
    else: 
        return render_template('newEvent.html', locations=locations)


# Edit an Event
@app.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
def editEvent(event_id):
    # Only logged in users can edit an event
    if 'username' not in login_session:
        return redirect('/login')
    # Get list of all cities to display in select menu
    cities = session.query(City).order_by(asc(City.name))   
    # Get Event information for event of interest 
    editedEvent = session.query(Event).filter_by(id=event_id).one()
    # Events can only be edited by the user that submitted the event
    if editedEvent.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not \
                authorized to delete this event.');}</script><body \
                onload='myFunction()''>"
    # Submit edits of event data
    if request.method == 'POST':
        # Format event date before submitting to database
        if request.form['event_date']:
            dt_obj = datetime.strptime(request.form['event_date'], '%Y-%m-%d')
            editedEvent.event_date = dt_obj
        if request.form['name']:
            editedEvent.name = request.form['name']
            app.logger.info(editedEvent.name)
        if request.form['description']:
            editedEvent.description = request.form['description']
            app.logger.info(editedEvent.description)
        if request.form['city_id']:
            editedEvent.city_id = request.form['city_id']
            app.logger.info(editedEvent.city_id)
        if request.form['event_url']:
            editedEvent.event_url = request.form['event_url']
            app.logger.info(editedEvent.event_url)
        if request.form['image_url']:
            editedEvent.image_url = request.form['image_url']
        session.add(editedEvent)
        session.commit()
        flash('Event Successfully Edited')
        return redirect(url_for('showEvent', city_id=editedEvent.city_id))
    else:
        return render_template('editEvent.html', event_id=event_id, 
                item=editedEvent, cities=cities)


# Delete an Event
@app.route('/event/<int:event_id>/delete', methods=['GET', 'POST'])
def deleteEvent(event_id):
    # Only logged in users can delete an event
    if 'username' not in login_session:
        return redirect('/login')
    eventToDelete = session.query(Event).filter_by(id=event_id).one()
    # Only user that submitted event can delete their event
    if eventToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not \
                authorized to delete this event.');}</script><body \
                onload='myFunction()''>"
    # Submit request to delete event
    if request.method == 'POST':
        session.delete(eventToDelete)
        session.commit()
        flash('Event Successfully Deleted')
        return redirect(url_for('showEvent', city_id=eventToDelete.city_id))
    else:
        return render_template('deleteEvent.html', item=eventToDelete)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    app.logger.info(login_session['provider'])
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            app.logger.info('Logout from Google Signin called')
            gdisconnect()
        if login_session['provider'] == 'facebook':
            app.logger.info('Logout from Facebook called')
            fbdisconnect()
        flash("You have successfully been logged out.")
        return redirect(url_for('showCities'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCities'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
