from app import db
from flask_login import UserMixin

# \dapted from an example found at: https://stackoverflow.com/questions/26606391/flask-login-attributeerror-user-object-has-no-attribute-is-active
class User(db.Model, UserMixin):
    id = db.Column(db.String(500), primary_key=True) # id = email for simplicity with flask login
    username = db.Column(db.String(50), unique=True, index=True)
    password = db.Column(db.String(100))
    enrolments = db.relationship('Enrolment', backref='user', lazy='dynamic')
    message = db.relationship('Message', backref='user', lazy='dynamic')
    vote = db.relationship('Vote', backref='user', lazy='dynamic')

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    module_code = db.Column(db.String(50))
    title = db.Column(db.String(50))
    course = db.Column(db.String(50))
    description = db.Column(db.String(1000))
    members = db.Column(db.Integer)
    enrolments = db.relationship('Enrolment', backref='module', lazy='dynamic')

class Enrolment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) # prevent UNIQUE constraint failed errors
    user_id = db.Column(db.String(100), db.ForeignKey('user.id'))
    module_id = db.Column(db.String(100), db.ForeignKey('module.id'))
    creator = db.Column(db.Boolean)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50))
    message = db.Column(db.String(5000)) 
    sender = db.Column(db.String(50), db.ForeignKey('user.id'))
    module = db.Column(db.Integer, db.ForeignKey('module.id'))
    time = db.Column(db.DateTime)
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    vote = db.relationship('Vote', backref='message', lazy='dynamic')

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(50), db.ForeignKey('user.id'))
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'))
    vote_type = db.Column(db.String(10))