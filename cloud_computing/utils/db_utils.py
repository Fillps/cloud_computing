# -*- coding: utf-8 -*-


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
