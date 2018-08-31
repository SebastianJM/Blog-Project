from app import app
from flask import flash, redirect, render_template, request, session, url_for, Blueprint
import datetime
from functools import wraps
from project import db
import re
import pymongo
from bson.json_util import dumps
from copy import deepcopy

entries_blueprint = Blueprint(
    'entries', __name__,
    template_folder='templates'
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
    
def noEntryFound():
    flash("Couldn't find the entry", "error")
    return redirect(url_for("entries.listEntries"))
    
@entries_blueprint.route('/entry',  methods = ['GET'])
@entries_blueprint.route('/entry/',  methods = ['GET'])
def listEntries():
    createEntryLink = url_for('entries.createEntry')
    entries = db.entries.find().sort([("date_creation", pymongo.DESCENDING)])
    data = deepcopy(entries)
    data = dumps(data)
    return render_template('listEntries.html', createEntryLink = createEntryLink, entries = entries, data = data);
    
@entries_blueprint.route('/entry/create', methods = ['GET', 'POST'])
@login_required
def createEntry():
    if request.method == 'GET':
        return render_template('createEntry.html')
    elif request.method == 'POST':
        link = re.sub('[^\w]+', '-', request.form['title'].lower())
        title = request.form['title']
        content = request.form['content']
        cover_image_url = request.form['cover_image_url']
        post = {
             "link": link,
             "cover_image_url": cover_image_url,
             "title": title,
             "content": content,
             "date_creation": datetime.datetime.utcnow() }
        if title is None:
            flash('Title not valid', 'error')
            return render_template('createEntry.html')
        findEntry = db.entries.find_one({"link": link})
        if findEntry is None:
            db.entries.insert_one(post)
        else:
            flash('Title already exists', 'error')
            return render_template('createEntry.html')
        return redirect(url_for("index"))
    else:
        return render_template('createEntry.html')
        
@entries_blueprint.route('/entry/<entryLink>/edit', methods = ['GET', 'POST'])
@login_required
def editEntry(entryLink):
    findEntry = db.entries.find_one({"link": entryLink})
    if findEntry is None:
        flash('Entry not found', 'error')
        return redirect(url_for("entries.noEntryFound"))
    if request.method == 'GET':
        return render_template('editEntry.html', entry = findEntry)
    elif request.method == 'POST':
        link = re.sub('[^\w]+', '-', request.form['title'].lower())
        title = request.form['title']
        content = request.form['content']
        cover_image_url = request.form['cover_image_url']
        post = {
             "link": link,
             "cover_image_url": cover_image_url,
             "title": title,
             "content": content,
             "date_creation": findEntry["date_creation"] }
        if title is None:
            flash('Title not valid', 'error')
            return render_template('editEntry.html', entry = post)
        newEntry = db.entries.find_one({"link": link})
        if newEntry is None or findEntry["link"] == link:
            db.entries.update({'_id': findEntry["_id"]}, {"$set": post}, upsert = False)
        else:
            flash('Title already exists', 'error')
            return render_template('editEntry.html', entry = post)
        return redirect(url_for("entries.listEntries"))
    else:
        return render_template('editEntry.html', entry = findEntry)
        
    
@entries_blueprint.route('/entry/<entryLink>', methods = ['GET', 'POST'])
def showEntry(entryLink):
    if entryLink is None or entryLink == '':
        return redirect(url_for("entries.noEntryFound"))
    entry = db.entries.find_one({"link": entryLink})
    if entry is None:
        return redirect(url_for("entries.noEntryFound"))
    data = deepcopy(entry)
    data = dumps(data)
    
    commentaries = db.commentaries.find({"entryLink": entryLink})
    return render_template('showEntry.html', entry = entry, entryjson = data, commentaries = commentaries)
    
@entries_blueprint.route('/entry/<entryLink>/addCommentary', methods = ['GET', 'POST'])
def addCommentary(entryLink):
    if 'user' not in request.form or 'comment' not in request.form or request.form['user'] == '' or request.form['comment'] == '':
        flash('Please, fill all the commentary fields', 'error')  
        return redirect(url_for("entries.showEntry", entryLink = entryLink))
    user = request.form['user']
    comment = request.form['comment']
    commentary = {
        'user': user,
        'comment': comment,
        'entryLink': entryLink
    }
    db.commentaries.insert_one(commentary)
    flash('Commentary successfully submitted', 'message')   
    return redirect(url_for("entries.showEntry", entryLink = entryLink))

@entries_blueprint.route('/entry/search', methods = ['GET', 'POST'])
def search():
    if 'query' not in request.form:
        flash('Please, enter a valid query', 'error')
        return redirect(url_for('entries.listEntries'))
    query = request.form['query']
    return redirect(url_for("entries.searchQuery", query = query))
    
@entries_blueprint.route('/entry/search/<query>', methods = ['GET', 'POST'])
def searchQuery(query):
    entries = db.entries.find({ '$or': [{"title": re.compile(query, re.IGNORECASE)}, {"content": re.compile(query, re.IGNORECASE)}]}).sort([("date_creation", pymongo.DESCENDING)])
    data = deepcopy(entries)
    data = dumps(data)
    total = entries.count()
    return render_template('search.html', entries = entries, data = data, query = query, total = total)
    
@entries_blueprint.route('/entry/<entryLink>/delete', methods = ['POST'])
@login_required
def deleteEntry(entryLink):
    db.entries.remove({"link": entryLink})
    flash('Entry was removed successfully!', 'message')
    return redirect(url_for("entries.listEntries"))
    
    
