import os
from random import seed, randint
from flask import Flask, render_template, request, redirect, session, url_for, abort, flash, jsonify, json
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps
from Changes import Changelog
from Admin import Admin
import datetime

KISS = Flask(__name__)
KISS.secret_key = os.environ.get('SECRET_KEY')
KISS.register_blueprint(Changelog)
KISS.register_blueprint(Admin)
KISS.config.update(dict(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME'),
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
))
mail = Mail(KISS)
bcrypt = Bcrypt(KISS)

client = MongoClient("mongodb+srv://"+str(os.environ.get('DB_USER'))+":"+str(os.environ.get('DB_PASSWORD'))+"@cluster0.azvnt.mongodb.net/kissDB?retryWrites=true&w=majority")
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

@KISS.route('/recovery', methods=['POST'])
def recovery():
    recoverFor = db.users.find_one({"Roll No": int(request.form['roll'])})
    senderName = recoverFor['Name']
    recipients = [request.form['roll']+"@gndu.ac.in"]

    msg = Message("[Project K.I.S.S.] Password Recovery Issue", sender=senderName, recipients=recipients)
    msg.body = "Hello There!!! \nWe recently recieved a request to change your password for your Project K.I.S.S. account. If that wasn't you, rest assured we won't do anything. But if it was indeed you, we urge you to reply to this email as soon as possible so that we can provide you that awesome experience again. \n \n- Project K.I.S.S. Dev, Keeping It Simple Stupid."
    mail.send(msg)
    return redirect('/')

@KISS.route('/json', methods=['GET', 'POST'])
def jsonApi():
    foundItems = db.items.find({"userRoll": session['roll']})
    listfound = list(foundItems)
    variable = json.loads(dumps(listfound))
    return jsonify({"items":variable})

@KISS.route('/playground', methods=['GET', 'POST'])
def playground():
    if 'username' in session:
        item=0
        defaultItem = {
            "userRoll": session['roll'],
            "listItems": [{"id": item, "name": "Sample List Item"}]
        }
        item=randint(0,1000)

        if request.method == "GET":
            date = datetime.datetime.now().strftime("%A, %b %d")            
            if db.items.count_documents({"userRoll": session['roll']}) == 0:
                db.items.insert_one(defaultItem)                
                return redirect('/playground')
            else:                
                return render_template('main.html', username=session['username'], role=session['role'], listTitle=date)
        else:            
            db.items.update_one({"userRoll": session['roll']}, {"$push": {"listItems": {"id": item, "name": request.form['newItem']}}})
            return "", 204
    else:
        abort(404)
    item=item+1

@KISS.route('/del', methods=['POST'])
def delete():
    checkedId = int(request.form['check'])
    db.items.update_one({"userRoll": session['roll']}, {"$pull": {"listItems": {"id": checkedId}}})
    return redirect('/playground')

@KISS.route('/demo')
def demo():
    return render_template('demo.html')

@KISS.route('/doc')
def doc():
    return render_template('doc.html')

@KISS.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'GET':
        return render_template('contact.html')
    else:
        feedback = {
            "Sender": request.form['senderName'],
            "Email": request.form['senderMail'],
            "Message": request.form['msg']
        }
        db.feedbacks.insert_one(feedback)
        return "", 204

@KISS.route('/reply', methods = ['POST'])
def reply():
    replyTo = db.feedbacks.find_one({"_id": ObjectId(request.form['id'])})
    senderName = replyTo['Sender']
    recipients = [replyTo['Email']]

    msg = Message("From Project K.I.S.S. Devs to "+senderName, sender=senderName, recipients=recipients)
    msg.body = request.form['reply']
    mail.send(msg)
    return redirect('/admin')

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
    return render_template('/submission.html')

client.close()

@KISS.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    KISS.run()