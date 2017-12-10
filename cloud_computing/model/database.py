# -*- coding: utf-8 -*-

from flask_security import SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy
from cloud_computing.model.models import User, Role

db = SQLAlchemy()

user_datastore = SQLAlchemyUserDatastore(db, User, Role)


def get_or_create(session, _model, **kwargs):
    """Returns a database instance. If there is none creates one."""
    instance = get(session, _model, **kwargs)

    if instance is None:
        instance = _model(**kwargs)
        session.add(instance)

    return instance


def get(session, _model, **kwargs):
    return session.query(_model).filter_by(**kwargs).first()
