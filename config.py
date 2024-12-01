import os

WTF_CSRF_ENABLED = True
SECRET_KEY = '3d08b789cbba790607acfe5c69a0804dda4000d863b27c20bfbb352933fd5300'

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True