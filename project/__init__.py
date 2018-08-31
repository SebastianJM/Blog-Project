from flask import Flask, request, redirect, url_for, render_template, flash, session, Blueprint
from pymongo import MongoClient
import pymongo
import datetime
from bson.json_util import dumps
from copy import deepcopy
from functools import wraps
from flask import Response

app = Flask(__name__)

client = MongoClient()
db = client.blogdb

app.secret_key = 'a'

# Admin credentials. This a very bad practice. This should be encrypted in a production version
first_username = "admin"
first_password = "admin"

from project.entries.__init__ import entries_blueprint
app.register_blueprint(entries_blueprint)

from project.settings.__init__ import settings_blueprint
app.register_blueprint(settings_blueprint)

from project.messages.__init__ import messages_blueprint
app.register_blueprint(messages_blueprint)

@app.context_processor
def utility_processor():
    blog_name = db.settings.find_one({"setting_type": "blog_name"})
    session['BLOG_NAME'] = blog_name['value'] if blog_name else 'MY NEW BLOG'
    author_name = db.settings.find_one({"setting_type": "author_name"})
    session['AUTHOR_NAME'] = author_name['value'] if author_name else 'AUTHOR NAME'
    brief_description = db.settings.find_one({"setting_type": "brief_description"})
    session['BRIEF_DESCRIPTION'] = brief_description['value'] if brief_description else 'This is your brief description. You can add some information about yourself, like: years of experience, hobbies, skills, your favourite icecream flavor, etc.'
    profile_picture = db.settings.find_one({"setting_type": "profile_picture"})
    session['PROFILE_PICTURE'] = profile_picture['value'] if profile_picture else 'https://profile.actionsprout.com/default.jpeg'
    social_networks = {}
    facebook = db.settings.find_one({"setting_type": "facebook"})
    if facebook is not None and facebook['value'] is not '':
        social_networks['FACEBOOK'] = facebook['value']
    twitter = db.settings.find_one({"setting_type": "twitter"})
    if twitter is not None and twitter['value'] is not '':
        social_networks['TWITTER'] = twitter['value']
    instagram = db.settings.find_one({"setting_type": "instagram"})
    if instagram is not None and instagram['value'] is not '':
        social_networks['INSTAGRAM'] = instagram['value']
    print(social_networks)
    session['SOCIAL_NETWORKS'] = social_networks
    footer = db.settings.find_one({"setting_type": "footer"})
    session['FOOTER'] = footer['value'] if footer else 'ALL RIGHTS RESERVED'
    
    return dict()

# Validator function for check if the user has permission to see admin pages (is logged in the system)
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to be logged to see this page')
            return redirect(url_for('index'))
    return wrap

# Routes
@app.route('/')
def index():
    #Response.delete_cookie('session', path='/')
    createEntryLink = url_for('entries.createEntry')
    entries = db.entries.find().sort([("date_creation", pymongo.DESCENDING)])
    data = deepcopy(entries)
    data = dumps(data)
    return render_template('listEntries.html', createEntryLink = createEntryLink, entries = entries, data = data)

@app.route('/about', methods = ['GET'])
def about():
    about_find = db.settings.find_one({"setting_type": "about"})
    if about_find is None:
        about_find = { "value": 'This is a longer text. Feel free of explain what is the blog going about and to tell something about yourself.' }
    
    data = deepcopy(about_find["value"])
    data = dumps(data)
    return render_template('about.html', about = about_find["value"], aboutjson = data)
    
@app.route('/login', methods = ['GET', 'POST'])
def login():
    username_find = db.settings.find_one({"setting_type": "username"})
    username = username_find['value'] if username_find else first_username
    password_find = db.settings.find_one({"setting_type": "password"})
    password = password_find['value'] if password_find else first_password
    login_credentials = {
        "username": username,
        "password": password
    }
    if request.method == 'GET':
        return render_template('login.html', login_credentials = login_credentials)
    elif request.method == 'POST':
        username_find = db.settings.find_one({"setting_type": "username"})
        username = username_find['value'] if username_find else first_username
        password_find = db.settings.find_one({"setting_type": "password"})
        password = password_find['value'] if password_find else first_password
        if(username == request.form['username'] and password == request.form['password']):
            flash('Logged in!', 'message')
            session['logged_in'] = True
            return redirect(url_for("index"))
        else:
            flash('Invalid credentials. Please, try again', 'error')
            return render_template('login.html', login_credentials = login_credentials)
    else:
        return render_template('login.html', login_credentials = login_credentials)
        
@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('Logged out!', 'message')
    return redirect(url_for("index"))
            
