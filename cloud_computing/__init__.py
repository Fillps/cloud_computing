# -*- coding: utf-8 -*-

from flask import Flask
from flask_heroku import Heroku

# Initialize Flask
app = Flask(__name__)
heroku = Heroku(app)

# Import configuration
app.config.from_pyfile('config.py')

from cloud_computing.model import db_setup
from cloud_computing.model import admin_setup
from cloud_computing.view import view

