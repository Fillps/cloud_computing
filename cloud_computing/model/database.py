# -*- coding: utf-8 -*-
from cloud_computing import app
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, utils

# Initialize SQLAlchemy
db = SQLAlchemy(app)

from cloud_computing.model.models import User, Role, ResourceRequests, Plan

# Initialize the SQLAlchemy data store and Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


def get(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        return None


def get_or_create(session, model, **kwargs):
    """Create a instance, unless they already exist returning the instance."""
    instance = get(session, model, **kwargs)
    if instance is None:
        instance = model(**kwargs)
        session.add(instance)
    return instance


@app.before_first_request
def before_first_request():
    """Creates test data before the app runs, should not go to production."""
    # Create any database tables that don't exist yet
    db.create_all()

    # Create the Roles "admin" and "end-user" -- unless they already exist
    user_datastore.find_or_create_role(name='admin',
                                       description='Administrator')
    user_datastore.find_or_create_role(name='end-user',
                                       description='End user')

    # Create two Users for testing purposes -- unless they already exists
    # In each case use Flask-Security utility function to encrypt the password
    encrypted_password = utils.hash_password('password')

    if not user_datastore.get_user('someone@example.com'):
        user_datastore.create_user(id=1,
                                   email='someone@example.com',
                                   password=encrypted_password)
    if not user_datastore.get_user('admin@example.com'):
        user_datastore.create_user(id=2,
                                   email='admin@example.com',
                                   password=encrypted_password)

    # Commit any database changes
    # The User and Roles must exist before we can add a Role to the User
    db.session.commit()

    # Set example of resource requests
    get_or_create(db.session, ResourceRequests, message='Teste de requisição de recurso',
                  user_id=1)
    get_or_create(db.session, ResourceRequests, message='Teste de requisição de recurso 2',
                  user_id=1)

    # Set example users roles
    user_datastore.add_role_to_user('someone@example.com', 'end-user')
    user_datastore.add_role_to_user('admin@example.com', 'admin')
    db.session.commit()

    # Create first test plans if they don't exist
    if not Plan.query.filter_by(title='Plano básico').first():
        basic_plan = Plan(title='Plano básico', price=19.99,
                          description='Descrição do plano básico')
        db.session.add(basic_plan)

    if not Plan.query.filter_by(title='Plano intermediário').first():
        intermediate_plan = Plan(title='Plano intermediário', price=29.99,
                                 description='Descrição do plano intermediário')
        db.session.add(intermediate_plan)

    if not Plan.query.filter_by(title='Plano avançado').first():
        advanced_plan = Plan(title='Plano avançado', price=49.99,
                             description='Descrição do plano avançado')
        db.session.add(advanced_plan)

    # Commit changes
    db.session.commit()
