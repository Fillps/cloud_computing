# -*- coding: utf-8 -*-
from flask_security import SQLAlchemyUserDatastore, Security
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from cloud_computing.model.models import User, Role
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = None


def get_or_create(session, model, **kwargs):
    """Create a instance, unless they already exist. Returns the created or found instance."""
    instance = session.query(model).filter_by(**kwargs).first()
    if instance is None:
        instance = model(**kwargs)
        session.add(instance)
    return instance


