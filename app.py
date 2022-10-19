from unicodedata import name
from flask import Flask, render_template, request, redirect, url_for, make_response
from dotenv import dotenv_values

import pymongo
import datetime
from bson.objectid import ObjectId
import sys

# instantiate the app
app = Flask(__name__)
# load credentials and configuration options from .env file
# if you do not yet have a file named .env, make one based on the template in env.example
config = dotenv_values(".env")

# turn on debugging if in development mode
if config['FLASK_ENV'] == 'development':
    # turn on debugging, if in development
    app.debug = True # debug mnode


# connect to the database
# cxn = pymongo.MongoClient(config['MONGO_URI'], serverSelectionTimeoutMS=5000)
# try:
#     # verify the connection works by pinging the database
#     cxn.admin.command('ping') # The ping command is cheap and does not require auth.
#     db = cxn[config['MONGO_DBNAME']] # store a reference to the database
#     print(' *', 'Connected to MongoDB!') # if we get here, the connection worked!
# except Exception as e:
#     # the ping command failed, so the connection is not available.
#     # render_template('error.html', error=e) # render the edit template
#     print(' *', "Failed to connect to MongoDB at", config['MONGO_URI'])
#     print('Database connection error:', e) # debug

#********** All Variables ***********************************#
currentUser = "-1"
def setvalue(n):
     global currentUser
     currentUser=n

#****************** All Routes ******************************#
# (DONE)
#route for homepage
@app.route('/')
def home():
    """
    Route for the home page
    """
    return render_template('index.html') # render the hone template

#***************************************************************#
# (DONE)
#route for login
@app.route('/login',methods=['POST','GET'])
def login_user():
    """
    Route for POST requests to login.
    Accepts the login information and check against the database.
    """
    name=request.form.get('name')
    password=request.form.get('password')
    if request.method=="GET":
        return render_template('login.html')
    else:
        if db.users.count_documents({'name':name, 'password':password}, limit = 1):
            setvalue(name)
            return render_template('create.html')
        else:
            return render_template('login.html')
        
#******************************************************************#    
# (DONE)
#route for signup
@app.route('/signup', methods=['POST','GET'])
def signupPage():
    """
    Route for GET request to get signup page.
    """
    if request.method=="GET":
        return render_template('signup.html')
    else:
        fname=request.form.get('fname')
        lname=request.form.get('lname')
        uname=request.form.get('uname')
        password=request.form.get('pass')
        if db.users.count_documents({'name':uname},limit=1):
            return render_template('signup.html')
        else:
            user={
                "name":uname,
                "password":password
            }
            db.users.insert_one(user);
            return render_template('login.html')

#***************************************************************#
# (DONE)        
#route for create
@app.route('/create',methods=['POST','GET'])
def create():
    """
    Route for POST requests to create contact.
    Accepts the login information and saves in the database.
    """
    if request.method=="GET":
        return render_template('create.html')
    else:
        name=request.form.get('name')
        state=request.form.get('state')
        areaCode=request.form.get('areaCode')
        number=request.form.get('number')
        remarks=request.form.get('remarks')

        #create a new document(contact) with the user entered data
        doc={
            "name":name,
            "state":state,
            "areaCode":areaCode,
            "number":number,
            "remarks":remarks,
            "created_at": datetime.datetime.utcnow(),
            "currentUser":currentUser
        }
        db.contactList.insert_one(doc) #insert a new document (contact)
        return render_template('create.html')

#****************************************************************#
# (DONE)
#route for contacts
@app.route('/contacts')
def contacts_list():
    """
    Route for GET request to see contacts.
    Shows all the contacts from the database.
    """
    docs = db.contactList.find({"currentUser":currentUser}).sort("created_at", -1) # sort in descending order of created_at timestamp
    return render_template('contacts.html',docs=docs)

#*****************************************************************#
# (NOT DONE)
#route for search
@app.route('/search',methods=['POST','GET'])
def search():
    """
    Route for GET and POST request to see contacts.
    Shows all the contacts from the database.
    """
    if request.method=='GET':
        return render_template('search.html')


#*****************************************************************#


# Notes:
# Create a route for favorites and update (NOT DONE)
# Front-end part not done