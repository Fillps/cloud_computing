# -*- coding: utf-8 -*-
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_security import RoleMixin, Security, \
    SQLAlchemyUserDatastore, UserMixin, utils
from sqlalchemy import func

from cloud_computing import app


# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Create a table to support many-to-many relationship between Users and Roles
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


def get(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        return None


class Role(db.Model, RoleMixin):
    """Definition of user role."""
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    # __str__ is required by Flask-Admin, so we can have human-readable
    # values for the Role when editing a User. If we were using Python 2.7,
    # this would be __unicode__ instead.
    def __str__(self):
        return self.name

    # __hash__ is required to avoid the exception TypeError: unhashable type:
    # 'Role' when saving a User
    def __hash__(self):
        return hash(self.name)


class User(db.Model, UserMixin):
    """Definition of user, fields are required by Flask-Security.

    Our User has six fields: ID, email, password, active, confirmed_at
    and roles. The roles field represents a many-to-many relationship
    using the roles_users table. Each user may have no role, one role,
    or multiple roles.
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean(), server_default='true')
    confirmed_at = db.Column(db.DateTime(), server_default=func.now())
    roles = db.relationship(
        'Role',
        secondary=roles_users,
        backref=db.backref('users', lazy='dynamic')
    )

    def __str__(self):
        return '<User id=%s email=%s>' % (self.id, self.email)


class Plan(db.Model):
    """Definition of plan."""
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), unique=True)
    price = db.Column(db.Float())
    description = db.Column(db.String(255))


class ResourceRequests(db.Model):
    """Definition of ResourceRequests"""
    id = db.Column(db.Integer(), primary_key=True)
    message = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message_date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    answer_date = db.Column(db.DateTime(timezone=True))


# Initialize the SQLAlchemy data store and Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


def get_or_create(session, model, **kwargs):
    """Create a instance, unless they already exist returning the instance."""
    instance = get(session, model, **kwargs)
    if instance is None:
        instance = model(**kwargs)
        session.add(instance)
    return instance


@app.before_first_request
def before_first_request():

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
    get_or_create(db.session, ResourceRequests, message='Hakjshdalksjh dlakjs hd lakjshda lksjhdadla kjshdal kjshdakljs'
                                                        'hdaklsjdhalk sjdhakljshdlakjshda lksjhdashdal kjlksh dakljsdha'
                                                        'klsjhdakljshdakljshdakl jshdalkdlkaj shdalksj dhalksj dhalkjsh'
                                                        'dalkjshfiu ohgsdpoifug hsdpfiouds oifjsodigjdpfoig jhsdpofighd'
                                                        'fgjasihdkla jshdaskljhalsk djhdjh aklsjdha lksjdhalkjs hlkaaj',
                                                        user_id=1)
    get_or_create(db.session, ResourceRequests, message='teste2', user_id=1)

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