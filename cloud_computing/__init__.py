#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Create application
from flask import Flask

app = Flask(__name__)

# Debugging configuration
app.config['SECRET_KEY'] = 'developer key'
app.debug = True

from cloud_computing.controller import *

