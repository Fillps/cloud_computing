# -*- coding: utf-8 -*-
from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy
from flask_security import utils

db = SQLAlchemy()
user_datastore = None
security = None

def get_or_create(session, model, **kwargs):
    """Create a instance, unless they already exist. Returns the created or found instance."""
    instance = session.query(model).filter_by(**kwargs).first()
    if instance is None:
        instance = model(**kwargs)
        session.add(instance)
    return instance


