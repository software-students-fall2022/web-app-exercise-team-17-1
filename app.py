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
cxn = pymongo.MongoClient(config['MONGO_URI'], serverSelectionTimeoutMS=5000)
try:
    # verify the connection works by pinging the database
    cxn.admin.command('ping') # The ping command is cheap and does not require auth.
    db = cxn[config['MONGO_DBNAME']] # store a reference to the database
    print(' *', 'Connected to MongoDB!') # if we get here, the connection worked!
except Exception as e:
    # the ping command failed, so the connection is not available.
    # render_template('error.html', error=e) # render the edit template
    print(' *', "Failed to connect to MongoDB at", config['MONGO_URI'])
    print('Database connection error:', e) # debug

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
            return redirect(url_for('create'))
        else:
            return render_template('loginError.html')
        
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
            return render_template('signupError.html')
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
        number=request.form.get('number')
        remarks=request.form.get('remarks')

        #create a new document(contact) with the user entered data
        doc={
            "name":name,
            "state":state,
            "number":number,
            "remarks":remarks,
            "created_at": datetime.datetime.utcnow(),
            "currentUser":currentUser,
            "favorite":"False"
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
# (DONE)
#route for search
@app.route('/search',methods=['POST','GET'])
def search():
    """
    Route for GET and POST request to see contacts.
    Shows all the contacts from the database.
    """
    if request.method=='GET':
        return render_template('search.html')
    if request.method=='POST':
        keyword = ""
        state = ""
        if(request.form.get('keyword') != ""):
            keyword = request.form.get('keyword')
        if(request.form.get('state') != ""):
            state = request.form.get('state')
        db.contactList.create_index([("name", "text")])
        if(keyword != "" and state != ""):
            docs = db.contactList.find({"currentUser": currentUser, "state": state, "name": {"$regex": keyword, "$options":"i"}}).sort("created_at", -1)
        elif(keyword != ""):
            docs = db.contactList.find({"currentUser": currentUser, "name": {"$regex": keyword, "$options":"i"}}).sort("created_at", -1)
        elif(state != ""):
            docs = db.contactList.find({"currentUser": currentUser, "state": state}).sort("created_at", -1)
        else:
            docs = db.contactList.find({"currentUser": currentUser}).sort("created_at", -1)
        return render_template('search.html', docs = docs)


#*****************************************************************#
# (NOT DONE)
@app.route('/favorite', methods=['POST','GET'])
def favorites():
     """
     Route for GET and POST request to see favorite contacts.
     Shows all the contacts from the database.
     """
     docs = db.contactList.find({"currentUser": currentUser, "favorite": "True"}).sort("created_at", -1)
     return render_template('favorites.html', docs = docs)


#******************************************************************#
# (DONE)
#route for editing/updating contacts
# route to view the edit form for an existing contact
@app.route('/edit/<mongoid>')
def edit(mongoid):
    """
    Route for GET requests to the edit page.
    Displays a form users can fill out to edit an existing record.
    """
    doc = db.contactList.find_one({"_id": ObjectId(mongoid)})
    return render_template('edit.html', mongoid=mongoid, doc=doc) # render the edit template

@app.route('/edit/<mongoid>', methods=['POST'])
def edit_contact(mongoid):
    """
    Route for POST requests to the edit page.
    Accepts the form submission data for the specified document and updates the document in the database.
    """
    name=request.form.get('name')
    state=request.form.get('state')
    number=request.form.get('number')
    remarks=request.form.get('remarks')
    doc = {
        "name":name,
        "state":state,
        "number":number,
        "remarks":remarks,
        "created_at":datetime.datetime.utcnow(),
        "currentUser":currentUser
    }
    if(request.form.get('favorite') != None):
        doc["favorite"] = request.form.get('favorite')
    else:
        doc["favorite"] = "False"
    db.contactList.update_one (
        {"_id": ObjectId(mongoid)}, # match criteria
        {"$set": doc}
    )
    return redirect(url_for('contacts_list')) # tell the browser to make a request for contacts_list

@app.route('/delete/<mongoid>', methods=['GET', 'POST'])
def delete(mongoid):
    """
    Route for GET requests to the delete page.
    Deletes the specified record from the database, and then redirects the browser to the home page.
    """
    if request.method == "GET":
        doc = db.contactList.find({"_id": ObjectId(mongoid)})
        return render_template('delete.html', mongoid=mongoid, doc=doc)
    if request.method == "POST":
        db.contactList.delete_one({"_id": ObjectId(mongoid)})
        return redirect(url_for('contacts_list')) # tell the web browser to make a request for the / route (the home function)