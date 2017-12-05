# -*- coding: utf-8 -*-
from flask_security import SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from cloud_computing.model.models import User, Role
user_datastore = SQLAlchemyUserDatastore(db, User, Role)


def get_or_create(session, _model, **kwargs):
    """Create a instance, unless they already exist. Returns the created or found instance."""
    instance = get(session, _model, **kwargs)
    if instance is None:
        instance = _model(**kwargs)
        session.add(instance)
    return instance


def get(session, _model, **kwargs):
    return session.query(_model).filter_by(**kwargs).first()

