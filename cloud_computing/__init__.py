# -*- coding: utf-8 -*-
from flask import Flask
from flask_admin import Admin
from flask_heroku import Heroku

from cloud_computing.model.models import User, Plan, Role, ResourceRequests
from cloud_computing.view.admin import UserAdmin, RoleAdmin, PlanAdmin, ResourceRequestsAdmin, ResourceRequestsUser


def create_app(config_filename):
    """Initialize Flask"""
    app = Flask(__name__)
    heroku = Heroku(app)

    # Import configuration
    app.config.from_pyfile(config_filename)

    from cloud_computing.model.database import db, user_datastore, security
    db.init_app(app)

    from flask_security import SQLAlchemyUserDatastore
    from flask_security import Security

    # Initialize the SQLAlchemy data store and Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)


    from cloud_computing.view.view import route_blueprint
    app.register_blueprint(route_blueprint)

    configFlaskAdmin(app)
    return app

def configFlaskAdmin(app):
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
    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(RoleAdmin(Role, db.session))
    admin.add_view(PlanAdmin(Plan, db.session))
    admin.add_view(ResourceRequestsAdmin(ResourceRequests, db.session, endpoint='resource-requests-admin'))
    admin.add_view(ResourceRequestsUser(ResourceRequests, db.session, endpoint='resource-requests-user'))
    return admin


