from app import db
from flask_login import UserMixin

# Adapted from an example found at: https://stackoverflow.com/questions/26606391/flask-login-attributeerror-user-object-has-no-attribute-is-active
class User(db.Model, UserMixin):
    id = db.Column(db.String(100), primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    enrolments = db.relationship('Enrolment', backref='user', lazy='dynamic')
    message = db.relationship('Message', backref='user', lazy='dynamic')
    vote = db.relationship('Vote', backref='user', lazy='dynamic')

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    module_code = db.Column(db.String(100))
    title = db.Column(db.String(100))
    description = db.Column(db.String(1000))
    members = db.Column(db.Integer)
    enrolments = db.relationship('Enrolment', backref='module', lazy='dynamic')

class Enrolment(db.Model):
    enrolment_id = db.Column(db.Integer, primary_key=True, autoincrement=True) # Prevent UNIQUE constraint failed errors
    user_id = db.Column(db.String(100), db.ForeignKey('user.id'))
    module_id = db.Column(db.String(100), db.ForeignKey('module.id'))
    creator = db.Column(db.Boolean)

class Message(db.Model):
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100))
    message = db.Column(db.String(5000)) 
    module = db.Column(db.String(100), db.ForeignKey('module.id'))
    sender = db.Column(db.String(100), db.ForeignKey('user.id'))
    time = db.Column(db.DateTime)
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    vote = db.relationship('Vote', backref='message', lazy='dynamic')

class Vote(db.Model):
    vote_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message_id = db.Column(db.Integer, db.ForeignKey('message.message_id'))
    vote_type = db.Column(db.String(10))