from app import app
from flask import flash, redirect, render_template, request, session, url_for, Blueprint
import datetime
from functools import wraps
from project import db
import re
import pymongo
from bson.json_util import dumps
from copy import deepcopy

settings_blueprint = Blueprint(
    'settings', __name__,
    template_folder ='templates'
)   

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.', 'error')
            return redirect(url_for('login'))
    return wrap
    
def updateSettingValue(setting_name, new_setting_value):
    new_setting = {
         "setting_type": setting_name,
         "value": new_setting_value }
    current_setting = db.settings.find_one({"setting_type": setting_name})
    if current_setting:
        db.settings.update({'_id': current_setting["_id"]}, {"$set": new_setting}, upsert = False)
    else:
        db.settings.insert_one(new_setting)
        
@settings_blueprint.route('/settings/general', methods = ['GET', 'POST'])
@login_required
def general():
    blog_name_find = db.settings.find_one({"setting_type": "blog_name"})
    blog_name = blog_name_find['value'] if blog_name_find else 'MY NEW BLOG'
    footer_find = db.settings.find_one({"setting_type": "footer"})
    footer = footer_find['value'] if footer_find else 'ALL RIGHTS RESERVED'
    general_settings = {
             "blog_name": blog_name,
             "footer": footer }
    if request.method == 'GET':
        return render_template('generalSettings.html', general_settings = general_settings)
    elif request.method == 'POST':
        new_blog_name = request.form['blog_name']
        general_settings["blog_name"] = new_blog_name
        updateSettingValue("blog_name", new_blog_name)
        
        new_footer = request.form['footer']
        general_settings["footer"] = new_footer
        updateSettingValue("footer", new_footer)
        
        flash('Changes saved!', 'message')
        return render_template('generalSettings.html', general_settings = general_settings)
    else:
        return render_template('generalSettings.html', general_settings = general_settings)
            
@settings_blueprint.route('/settings/profile', methods = ['GET', 'POST'])
@login_required
def profile():
    author_name_find = db.settings.find_one({"setting_type": "author_name"})
    author_name = author_name_find['value'] if author_name_find else 'AUTHOR NAME'
    brief_description_find = db.settings.find_one({"setting_type": "brief_description"})
    brief_description = brief_description_find['value'] if brief_description_find else 'This is your brief description. You can add some information about yourself, like: years of experience, hobbies, skills, your favourite icecream flavor, etc.'
    about_find = db.settings.find_one({"setting_type": "about"})
    about = about_find['value'] if author_name_find else 'This is a longer text. Feel free of explain what is the blog going about and to tell something about yourself.'
    profile_picture_find = db.settings.find_one({"setting_type": "profile_picture"})
    profile_picture = profile_picture_find['value'] if profile_picture_find else 'https://profile.actionsprout.com/default.jpeg'
    facebook_find = db.settings.find_one({"setting_type": "facebook"})
    facebook = facebook_find['value'] if facebook_find else None
    twitter_find = db.settings.find_one({"setting_type": "twitter"})
    twitter = twitter_find['value'] if twitter_find else None
    instagram_find = db.settings.find_one({"setting_type": "instagram"})
    instagram = instagram_find['value'] if instagram_find else None
    profile_settings = {
        "author_name": author_name,
        "brief_description": brief_description,
        "about": about,
        "profile_picture": profile_picture,
        "facebook": facebook,
        "twitter": twitter,
        "instagram": instagram
    }
    if request.method == 'GET':
        return render_template('profileSettings.html', profile_settings = profile_settings)
    elif request.method == 'POST':
        new_author_name = request.form['author_name']
        profile_settings["author_name"] = new_author_name
        updateSettingValue("author_name", new_author_name)
        
        new_brief_description = request.form['brief_description']
        profile_settings["brief_description"] = new_brief_description
        updateSettingValue("brief_description", new_brief_description)
        
        new_about = request.form['about']
        profile_settings["about"] = new_about
        updateSettingValue("about", new_about)
        
        new_profile_picture = request.form['profile_picture']
        profile_settings["profile_picture"] = new_profile_picture
        updateSettingValue("profile_picture", new_profile_picture)
        
        new_facebook = request.form['facebook']
        profile_settings["facebook"] = new_facebook
        updateSettingValue("facebook", new_facebook)
        
        new_twitter = request.form['twitter']
        profile_settings["twitter"] = new_twitter
        updateSettingValue("twitter", new_twitter)
        
        new_instagram = request.form['instagram']
        profile_settings["instagram"] = new_instagram
        updateSettingValue("instagram", new_instagram)
        
        flash('Changes saved!', 'message')
        return render_template('profileSettings.html', profile_settings = profile_settings)
    else:
        return render_template('profileSettings.html', profile_settings = profile_settings)

@settings_blueprint.route('/settings/account', methods = ['GET', 'POST'])
@login_required
def account():
    username_find = db.settings.find_one({"setting_type": "username"})
    username = username_find['value'] if username_find else ''
    account_settings = {
        "username": username
    }
    if request.method == 'GET':
        return render_template('accountSettings.html', account_settings = account_settings)
    elif request.method == 'POST':
        error = False
        new_username = request.form['username']
        if new_username is None or new_username == '':
            error = True
            flash('Username cannot be empty!', 'error')
        else:
            account_settings["username"] = new_username
            updateSettingValue("username", new_username)
        
        new_password = request.form['password']
        new_repeat_password = request.form['password']
        if new_password == new_repeat_password and new_password != '':
            updateSettingValue("password", new_password)
        else:
            error = True
            flash("Passwords don't coincide or are empty!", 'error')
        if error is False:
            flash('Changes saved!', 'message')
        return render_template('accountSettings.html', account_settings = account_settings)
    else:
        return render_template('accountSettings.html', account_settings = account_settings)