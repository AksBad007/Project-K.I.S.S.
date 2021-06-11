import os
from flask import Flask, render_template, request, redirect, session, url_for, abort, flash
from flask_session import Session
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from bson.objectid import ObjectId
from Changes import Changelog
from Admin import Admin
import datetime

KISS = Flask(__name__)
KISS.secret_key = os.environ.get('SECRET_KEY')

KISS.register_blueprint(Changelog)
KISS.register_blueprint(Admin)

bcrypt = Bcrypt(KISS)

client = MongoClient("mongodb+srv://"+os.environ.get('DB_USER')+":"+os.environ.get('y')+"@cluster0.azvnt.mongodb.net/kissDB?retryWrites=true&w=majority")
db = client["kissDB"]

@KISS.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username'], role=session['role'])
    return render_template('index.html')

@KISS.route('/login', methods=['POST'])
def login():
    rollNo = int(request.form["roll"])
    password = request.form["password"]
    foundUser = db.users.find_one({'Roll No': rollNo})

    if(db.users.count_documents({'Roll No': rollNo}, limit = 1) != 0):
        if(bcrypt.check_password_hash(foundUser["Password"], password)):
            session["username"] = foundUser["Name"]
            session["roll"] = foundUser["Roll No"]
            session["role"] = foundUser["Role"]
            return redirect(url_for('index'))
        else:
            abort(404)
    else:
        abort(404)

@KISS.route('/edit', methods=['GET', 'POST'])
def edit():
    foundUser = db.users.find_one({'Roll No': session['roll']})

    if request.method == "GET":
        if 'username' in session:
            return render_template('edit.html', username=session['username'], roll=session['roll'])
        else:
            abort(404)
    else:
        newName = request.form['newName']
        newPass = bcrypt.generate_password_hash(request.form['newPass'])
        db.users.update_one({'Name': session['username']}, {'$set': {'Name': newName, 'Password': newPass}})
        session['username'] = newName
        flash('User Info Updated')
        return redirect('/edit')

@KISS.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('roll', None)
    session.pop('role', None)
    return redirect(url_for('index'))

@KISS.route('/signup', methods=['POST'])
def signup():
    newUser = {
        "Name": request.form['name'],
        "Roll No": int(request.form["roll"]),
        "Password": bcrypt.generate_password_hash(request.form["password"]),
        "Role": "Member"
    }

    if(db.users.count_documents({'Roll No': int(request.form["roll"])}, limit = 1) != 0):
        return render_template('already_signed.html')
    else:
        db.users.insert_one(newUser)
        session["username"] = request.form['name']
        session["roll"] = int(request.form["roll"])
        session["role"] = "Member"
        return redirect('/')

@KISS.route('/playground', methods=['GET', 'POST'])
def playground():
    if 'username' in session:
        item=0
        defaultItem = { 
            "userRoll": session['roll'],
            "listItems": [{"id": item, "name": "Sample List Item"}]
        }
        item+=1

        if request.method == "GET":
            date = datetime.datetime.now().strftime("%A, %b %d")
            foundItems = db.items.find({"userRoll": session['roll']})
            
            if db.items.count_documents({"userRoll": session['roll']}) == 0:
                db.items.insert_one(defaultItem)                
                return redirect('/playground')
            else:
                return render_template('main.html', username=session['username'], role=session['role'], listTitle=date, ListItems=foundItems)
        else:
            item+=1
            db.items.update_one({"userRoll": session['roll']}, {"$push": {"listItems": {"id": item, "name": request.form['newItem']}}})            
            return "", 204
    else:
        abort(404)

@KISS.route('/del', methods=['POST'])
def delete():
    checkedId = request.form['check']
    db.items.delete_many({"_id": ObjectId(checkedId)})
    return "", 204

@KISS.route('/demo')
def demo():
    return render_template('demo.html')

@KISS.route('/doc')
def doc():
    return render_template('doc.html')

@KISS.route('/submission', methods=['GET','POST'])
def submit():
    if request.method == "POST":
        submission = {
            "Name": request.form["mdName"],
            "Title": request.form['mdTitle'],
            "Link": request.form['mdLink'],
            "Description": request.form['mdDesc'],
            "Status": "Pending"
        }
        db.submissions.insert_one(submission)
        return "", 204
    else:
        return render_template('/submission.html')

client.close()

@KISS.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    KISS.run()