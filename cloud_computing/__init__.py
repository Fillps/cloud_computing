# -*- coding: utf-8 -*-

from flask import Flask

# Initialize Flask
app = Flask(__name__)

# Import configuration
app.config.from_pyfile('config.py')

from cloud_computing.model import db_setup
from cloud_computing.model import admin_setup
from cloud_computing.view import view
