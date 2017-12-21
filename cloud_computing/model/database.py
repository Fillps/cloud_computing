# -*- coding: utf-8 -*-

from flask_security import SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from cloud_computing.model.models import User, Role

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
