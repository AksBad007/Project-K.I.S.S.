from flask import Blueprint, render_template, redirect, request, url_for
from pymongo import MongoClient

Changelog = Blueprint('Changelog', __name__, url_prefix='/changes')

client = MongoClient('localhost', 27017)
db = client.kissDB

@Changelog.route('/', methods=['GET'])
def changePage():
    return render_template('changes.html', changes=db.changes.find())

@Changelog.route('/add', methods=['GET', 'POST'])
def addChange():
    if request.method == "GET":
        return render_template('addChange.html')
    else:
        newChange = {"ver": "----------"+request.form['ver']+"----------", "desc": request.form['desc']}
        db.changes.insert_one(newChange)
        return redirect(url_for('Changelog.changePage'))