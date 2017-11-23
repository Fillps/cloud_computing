# -*- coding: utf-8 -*-
from flask import current_app as app
from flask_security import RoleMixin, UserMixin, SQLAlchemyUserDatastore, Security
from sqlalchemy import func
from cloud_computing.model.database import db


# Create a table to support many-to-many relationship between Users and Roles
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


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


