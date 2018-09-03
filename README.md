# Flask Blog

Blog web application built using Python with Flask and MongoDB. Participant of the contest [HackerEarth Beginner Hack 2.0](https://www.hackerearth.com/sprints/beginner-hack-20) 

## Getting Started

These instructions will get you a copy of the project up and running on your local machine with Ubuntu installed for development and testing purposes.

## Prerequisites

You must have Python 3 installed.
```
$ sudo apt-get install python3
```
Also, the Python's Virtual Environment module,
```
$ sudo apt-get install python3-venv
```
the Flask Framework,
```
$ sudo pip install flask
```
the Python development kit,
```
$ sudo apt-get install build-essential python-dev
```
MongoDB,
```
$ sudo apt-get install -y mongodb-org
```
and finally, Pymongo (Bridge between Python and MongoDB)
```
$ sudo python3 -m pip install pymongo
```

## Installing

After clonning the project, move to the *blog* folder and initialize the virtual environment
```
python3 -m venv venv
```

## Running

Initialize the MongoDB service
```
mongod
```
In another console, activate the virtual environment
```
source venv/bin/activate
```
Run the Flask application
```
python app.py
```
Now the application is running in your localhost. Happy browsing!

## Built With

* [Flask](http://flask.pocoo.org/) - Microframework for Python based on Werkzeug, Jinja 2 and good intentions
* [MongoDB](https://www.mongodb.com) - The world’s leading database for modern applications


