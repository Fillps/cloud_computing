# -*- coding: utf-8 -*-
from flask import Flask
from flask_admin import Admin
from flask_heroku import Heroku


def create_app(config_filename='../configs/production.py'):
    """Initialize Flask"""
    app = Flask(__name__)

    # Setup heroku
    Heroku(app)

    # Import configuration
    app.config.from_pyfile(config_filename)

    config_database(app)
    config_flask_admin(app)
    config_blueprints(app)

    return app


def config_flask_admin(app):
    # Initialize Flask-Admin
    admin = Admin(
        app,
        'Management',
        base_template='admin.html',
        template_mode='bootstrap3',
        url='/manage'
    )

    # Add Flask-Admin views for Users and Roles
    from cloud_computing.model.database import db
    from cloud_computing.model import models
    from cloud_computing.view import admin as _adm

    admin.add_view(_adm.UserAdmin(models.User, db.session))
    admin.add_view(_adm.RoleAdmin(models.Role, db.session))
    admin.add_view(_adm.PlanAdmin(models.Plan, db.session))
    admin.add_view(_adm.ResourceRequestsAdmin(models.ResourceRequests, db.session, endpoint='resource-requests-admin'))
    admin.add_view(_adm.ResourceRequestsUser(models.ResourceRequests, db.session, endpoint='resource-requests-user'))
    return admin


def config_database(app):
    from cloud_computing.utils import db_utils
    from cloud_computing.model.database import db, user_datastore, security
    from cloud_computing.model.models import User, Role
    from flask_security import SQLAlchemyUserDatastore
    from flask_security import Security

    db.init_app(app)

    # Initialize Flask-Security
    security = Security(app, user_datastore)

    db_utils.setup_database(app)


def config_blueprints(app):
    from cloud_computing.view.view import default_blueprint
    app.register_blueprint(default_blueprint)
