from app import app
from flask import flash, redirect, render_template, request, session, url_for, Blueprint
import datetime
from functools import wraps
from project import db
import re
import pymongo
from bson.json_util import dumps
from copy import deepcopy
from bson.objectid import ObjectId

messages_blueprint = Blueprint(
    'messages', __name__,
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


    
@messages_blueprint.route('/message/create', methods = ['GET', 'POST'])
def create():
    if request.method == 'GET':
        return render_template('createMessage.html')
    elif request.method == 'POST':
        subject = request.form['subject']
        email = request.form['email']
        message = request.form['message']
        message_to_send = {
             "subject": subject,
             "email": email,
             "message": message,
             "read": False,
             "date_creation": datetime.datetime.utcnow()}

        db.messages.insert_one(message_to_send)
        flash('Message sent!', 'message')
        return redirect(url_for("entries.listEntries"))
    else:
        return render_template('createMessage.html')
        
@messages_blueprint.route('/message', methods = ['GET'])
@login_required
def listMessages():
    messages = db.messages.find().sort([("date_creation", pymongo.DESCENDING)])
    total = messages.count()
    return render_template('listMessages.html', messages = messages, total = total);
    
@messages_blueprint.route('/message/', methods = ['GET'])
def noMessageFound():
    flash("Couldn't find the personal message", "error")
    return redirect(url_for("messages.listMessages"))
    
@messages_blueprint.route('/message/<messageLink>', methods = ['GET'])
@login_required
def showMessage(messageLink):
    if messageLink is None or messageLink == '':
        return redirect(url_for("messages.noMessageFound"))
    message = db.messages.find_one({"_id": ObjectId(messageLink)})
    if message is None:
        return redirect(url_for("messages.noMessageFound"))
    if message['read'] == False:
        print("iNASD")
        message['read'] = True
        db.messages.update({'_id': ObjectId(messageLink)}, {"$set": message}, upsert = False)
    return render_template('showMessage.html', message = message)

@messages_blueprint.route('/message/search', methods = ['GET', 'POST'])
def search():
    if 'query' not in request.form:
        flash('Please, enter a valid query', 'error')
        return redirect(url_for('messages.listMessages'))
    query = request.form['query']
    return redirect(url_for("messages.searchQuery", query = query))

@messages_blueprint.route('/message/search/<query>', methods = ['GET', 'POST'])
def searchQuery(query):
    messages = db.messages.find({ '$or': [{"subject": re.compile(query, re.IGNORECASE)}, {"message": re.compile(query, re.IGNORECASE)}, {"email": re.compile(query, re.IGNORECASE)}]}).sort([("date_creation", pymongo.DESCENDING)])
    total = messages.count()
    return render_template('searchMessages.html', messages = messages, query = query, total = total)