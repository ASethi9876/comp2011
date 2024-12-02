import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user
from app import app, db, models, bcrypt
from app.models import User, Module, Enrolment, Message, Vote
from datetime import datetime
from config import SQLALCHEMY_DATABASE_URI
import os.path

class TestCase(unittest.TestCase):
   def setUp(self):
      app.config.from_object('config')
      app.config['TESTING'] = True
      app.config['WTF_CSRF_ENABLED'] = False

      app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
      self.app = app.test_client()

      # use of app.context adapted from: https://stackoverflow.com/questions/73961938/flask-sqlalchemy-db-create-all-raises-runtimeerror-working-outside-of-applicat
      with app.app_context():
         db.create_all()
         hashed_password = bcrypt.generate_password_hash("testing1").decode('utf-8') 
         user = User(id="user@test",username="test",password=hashed_password)
         db.session.add(user)
         db.session.commit()

      pass

   def tearDown(self):
      with app.app_context():
         db.session.remove()
         db.drop_all()

   def test_loginroute(self):
      response = self.app.get('/',
                           follow_redirects=True)
      self.assertEqual(response.status_code, 200)

   def test_registerroute(self):
      response = self.app.get('/register',
                           follow_redirects=True)
      self.assertEqual(response.status_code, 200)
      
   def test_homeroute_nologin(self):
      response = self.app.get('/home',
                           follow_redirects=True)
      self.assertEqual(response.status_code, 401)

   def test_writemessageroute_nologin(self):
      response = self.app.get('/new_message',
                           follow_redirects=True)
      self.assertEqual(response.status_code, 401)

   def test_modulelistroute_nologin(self):
      response = self.app.get('/module_list',
                           follow_redirects=True)
      self.assertEqual(response.status_code, 401)
   
   def test_createmoduleroute_nologin(self):
      response = self.app.get('/create_module',
                           follow_redirects=True)
      self.assertEqual(response.status_code, 401)

   def test_user(self):
      with app.app_context():
         user = User(id="abc@test.com",username="test1",password="12345678")
         db.session.add(user)
         db.session.commit()
         assert user in db.session

   def test_module(self):
      with app.app_context():
         module = Module(module_code="COMP1234",title="Test",course="Test",description="Testing",members=1)
         db.session.add(module)
         db.session.commit()
         assert module in db.session

   def test_enrolment(self):
      with app.app_context():
         enrolment = Enrolment(user_id="abc@test.com",module_id="test",creator=True)
         db.session.add(enrolment)
         db.session.commit()
         assert enrolment in db.session
   
   def test_message(self):
      with app.app_context():
         time = datetime.now()
         message = Message(title="Test",message="Testing",sender="abc@test.com",module=1,time=time,upvotes=1,downvotes=1)
         db.session.add(message)
         db.session.commit()
         assert message in db.session

   def test_vote(self):
      with app.app_context():
         vote = Vote(user_id="abc@test.com",message_id=1,vote_type="up")
         db.session.add(vote)
         db.session.commit()
         assert vote in db.session

if __name__ == '__main__':
    unittest.main()