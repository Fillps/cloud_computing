# -*- coding: utf-8 -*-

from flask_security import SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from cloud_computing.model.models import User, Role

user_datastore = SQLAlchemyUserDatastore(db, User, Role)


# TODO @Filipe Eu não entendi como essas duas funções se complementam,
# o que é essa instância e quando tu tem que criar?
# Acho que ficaria mais claro se a cada interação com o banco tu
# primeiro criasse a instância e depois operasse em cima dela, o que tu acha?

def get_or_create(session, _model, **kwargs):
    """Returns a database instance. If there is none creates one."""
    instance = get(session, _model, **kwargs)

    if instance is None:
        instance = _model(**kwargs)
        session.add(instance)

    return instance


def get(session, _model, **kwargs):
    """Queries the database instance in the session."""
    return session.query(_model).filter_by(**kwargs).first()
