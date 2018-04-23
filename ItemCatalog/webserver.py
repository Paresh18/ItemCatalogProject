from flask import Flask, render_template
from flask import request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine
from flask import session as login_session
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Items, User
from sqlalchemy.orm.exc import NoResultFound
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "ItemCatalog"

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    if 'username' in login_session:
        return redirect(url_for('Home'))
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code, now compatible with Python3
    request.get_data()
    code = request.data.decode('utf-8')

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # Submit request, parse response - Python3 compatible
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is \
        already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
      
 
    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id
  
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
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
    output += ' " style = "width: 300px; height: 300px; \
              border-radius: 150px;-webkit-border-radius:\
                  150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
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

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        print result['status']
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# This Page display the Categories and the varoius items
@app.route('/')
def Home():
    list = []
    listname = []
    itemname = []
    dict = {}
    out = ''

# if not login then the below code will run
    category = session.query(Category).all()
    item = session.query(Items).all()

    for i in item:
        itemname.append(i.name)

    for i in item:
        list.append(i.category_id)
    for i in list:
        finalid = session.query(Category).filter_by(id=i).one()
        listname.append(finalid.name)
    for i, k in zip(itemname, listname):
        dict[i] = k
    if 'username' in login_session:
        print "login"
        return render_template('home.html', category=category,
                               item=item, dict=dict, 
                               usernamevalue=login_session["username"])
    else:
        return render_template('home.html', category=category, 
                               item=item, dict=dict)


# This page give the item related to particulat category
@app.route('/category/<int:category_id>/item')
def SelectedcategoryItem(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Items).filter_by(category_id=category_id).all()
    print items
    return render_template('selectedcategoryitem.html', 
                           items=items, category=category)

# Creating new Item in ItemList for the Category
@app.route('/category/new/', methods=['GET', 'POST'])
def NewCreateItem():
    output = ''
    if 'username' not in login_session:
        print "Not login"
        return redirect('/login')
    # if not login than make it login send it to the login.html
    if request.method == 'POST':
        newItem = Items(name=request.form['name'], 
                        description=request.form['desc'], 
                        category_id=request.form.get('category_select'),
                        user_id=login_session["user_id"])
        session.add(newItem)
        session.commit()
        return redirect(url_for('Home'))
    else:
        return render_template('NewCreateItem.html')

# this is the section to display description of an item


@app.route('/menuitem/<string:menuitem>/description/', methods=['GET', 'POST'])
def MenuItemdescription(menuitem):
    items = session.query(Items).filter_by(name=menuitem).one()
    if 'username' not in login_session:
        return render_template('MenuItemdescription.html', items=items)
    else:
        return render_template('MenuItemdescription.html', items=items, 
                               usernamevalue=login_session['username'])

# this is the section to edit the item


@app.route('/menuitem/<int:menuitemid>/edit/', methods=['GET', 'POST'])
def EditItem(menuitemid):
    edititem = session.query(Items).filter_by(id=menuitemid).one()
    if request.method == 'POST':
        edititem.name = request.form['name']
        edititem.description = request.form['desc']
        edititem.category_id = request.form.get('category_select')
        edititem.user_id = login_session["user_id"]
        session.add(edititem)
        session.commit()
        return redirect(url_for('Home'))
    if 'username' not in login_session:
        return redirect(url_for('Home'))
    else:
        return render_template('EditItem.html', edititemId=edititem)

# This gives the json file for category

#Gives jsonfile for all categories
@app.route('/category/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])

#Gives jsonfile for all items
@app.route('/items/JSON')
def ItemsJSON():
    items = session.query(Items).all()
    return jsonify(items=[r.serialize for r in items])

#Gives jsonfile for all items related to a category 
@app.route('/category/<int:category_id>/item/JSON')
def SelectedcategoryItemJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Items).filter_by(category_id=category_id).all()
    return jsonify(categories=[r.serialize for r in items])


# this is the section to delete the item
@app.route('/deleteitem/<int:menuitemid>/delete', methods=['GET', 'POST'])
def DeleteItem(menuitemid):
    deleteitem = session.query(Items).filter_by(id=menuitemid).one()
    if request.method == 'POST':
        session.delete(deleteitem)
        session.commit()
        return redirect(url_for('Home'))
    if 'username' not in login_session:
        return redirect(url_for('Home'))
    else:
        return render_template('DeleteItem.html', deleteitem=deleteitem)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='localhost', port=3000)
