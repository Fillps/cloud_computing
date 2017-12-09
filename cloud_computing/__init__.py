# -*- coding: utf-8 -*-
from flask import Flask
from flask_admin import Admin
from flask_heroku import Heroku
from flask_admin.menu import BaseMenu, MenuView

from cloud_computing.model.database import db, user_datastore


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
    from cloud_computing.model import models
    from cloud_computing.view import admin as _adm, end_user as _user

    admin.add_view(_adm.UserAdmin(models.User, db.session))
    admin.add_view(_adm.RoleAdmin(models.Role, db.session))
    admin.add_view(_adm.PlanAdmin(models.Plan, db.session))
    admin.add_view(_adm.ResourceRequestsAdmin(models.ResourceRequests, db.session, endpoint='resource-requests-admin'))
    admin.add_view(_adm.CpuAdmin(models.Cpu, db.session, category='Componentes'))
    admin.add_view(_adm.GpuAdmin(models.Gpu, db.session, category='Componentes'))
    admin.add_view(_adm.RamAdmin(models.Ram, db.session, category='Componentes'))
    admin.add_view(_adm.HdAdmin(models.Hd, db.session, category='Componentes'))

    admin.add_view(_user.CreditCardUser(models.CreditCard, db.session))
    admin.add_view(_user.PurchaseUser(models.Purchase, db.session))
    admin.add_view(_user.ResourceRequestsUser(models.ResourceRequests, db.session, endpoint='resource-requests-user'))
    return admin


def config_database(app):

    db.init_app(app)
    config_flask_security(app)

    from cloud_computing.utils import db_utils
    db_utils.setup_database(app)


def config_flask_security(app):
    # Initialize Flask-Security
    from flask_security import Security
    from cloud_computing.view.security import ExtendedRegisterForm
    Security(app, user_datastore, register_form=ExtendedRegisterForm)

    from flask_security import user_registered

    @user_registered.connect_via(app)
    def user_registered_sighandler(sender, **extra):
        user = extra.get('user')
        role = user_datastore.find_or_create_role('end-user')
        user_datastore.add_role_to_user(user, role)
        db.session.commit()


def config_blueprints(app):
    from cloud_computing.view.view import default_blueprint
    app.register_blueprint(default_blueprint)