# -*- coding: utf-8 -*-

from flask_security import SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy
from flask_whooshee import Whooshee

db = SQLAlchemy()
whooshee = Whooshee()

from cloud_computing.model.models import User, Role

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
