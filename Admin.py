import os
from flask import Blueprint, render_template, redirect, session, abort
from pymongo import MongoClient

Admin = Blueprint('Admin', __name__, url_prefix = '/admin')

client = MongoClient("mongodb+srv://"+str(os.environ.get(DB_USER))+":"+str(os.environ.get(DB_PASSWORD))+"@cluster0.azvnt.mongodb.net/kissDB?retryWrites=true&w=majority")
db = client["kissDB"]

userNo = db.users.count_documents({})
users = db.users.find()
submits = db.submissions.find()
feedbacks = db.feedbacks.find()
changeNo = db.changes.count_documents({})
submitNo = db.submissions.count_documents({})
feedbackNo = db.feedbacks.count_documents({})

@Admin.route('/')
def admin():
    if 'username' not in session or session['role'] == 'Member':
        abort(404)
    return render_template('admin.html', username=session['username'], users=users, userNo=userNo, changeNo=changeNo, submitNo=submitNo, submits=submits, feedbackNo=feedbackNo, feedbacks=feedbacks)

@Admin.route('/db')
def db():
    return redirect("https://cloud.mongodb.com/v2/60bfbb8e06e7b925bf0e951c#metrics/replicaSet/60bfbc7a34ca63114c540108/explorer/kissDB")