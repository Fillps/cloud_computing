# -*- coding: utf-8 -*-
import warnings

from flask import Flask
from flask_admin import Admin
from flask_heroku import Heroku
from flask_security import Security
from flask_security import user_registered

from cloud_computing.model.database import db, user_datastore
from cloud_computing.model import models
from cloud_computing.view import admin as _adm, end_user as _user
from cloud_computing.utils import db_utils
from cloud_computing.view.register import ExtendedRegisterForm
from cloud_computing.view.view import default_blueprint


class AppFactory:
    """Builds the app."""
    def __init__(self, config_filename='../configs/production.py'):
        self.app = Flask(__name__)

        Heroku(self.app)
        self.app.config.from_pyfile(config_filename)

        self.__config_database_and_security()
        self.__config_flask_admin()
        self.__config_blueprints()

        @user_registered.connect_via(self.app)
        def user_registered_sighandler(sender, **extra):
            """Adds the end-user role to the user upon registering."""
            user = extra.get('user')
            role = user_datastore.find_or_create_role('end-user')
            user_datastore.add_role_to_user(user, role)
            db.session.commit()

    def get_app(self):
        return self.app

    def __config_flask_admin(self):
        admin = Admin(
            self.app,
            'Management',
            base_template='admin.html',
            template_mode='bootstrap3',
            url='/manage'
        )

        admin.add_view(_adm.UserAdmin(models.User, db.session))
        admin.add_view(_adm.RoleAdmin(models.Role, db.session))
        admin.add_view(_adm.PlanAdmin(models.Plan, db.session))
        admin.add_view(_adm.ResourceRequestsAdmin(
            models.ResourceRequests,
            db.session,
            endpoint='resource-requests-admin'))
        admin.add_view(_adm.CpuAdmin(models.Cpu, db.session,
                                     category='Componentes'))
        admin.add_view(_adm.GpuAdmin(models.Gpu, db.session,
                                     category='Componentes'))
        admin.add_view(_adm.RamAdmin(models.Ram, db.session,
                                     category='Componentes'))
        admin.add_view(_adm.HdAdmin(models.Hd, db.session,
                                    category='Componentes'))

        admin.add_view(_adm.ServerAdmin(
            models.Server,
            db.session,
            category='Servidores'))

        with warnings.catch_warnings():
            warnings.filterwarnings('ignore',
                                    'Fields missing from ruleset',
                                    UserWarning)
            admin.add_view(_adm.ServerGpu(models.ServerGpu,
                                          db.session,
                                          category='Servidores'))
            admin.add_view(_adm.ServerRam(models.ServerRam,
                                          db.session,
                                          category='Servidores'))
            admin.add_view(_adm.ServerHd(models.ServerHd,
                                         db.session,
                                         category='Servidores'))

        admin.add_view(_user.CreditCardUser(models.CreditCard, db.session))
        admin.add_view(_user.PurchaseUser(models.Purchase, db.session))
        admin.add_view(_user.ResourceRequestsUser(
            models.ResourceRequests,
            db.session,
            endpoint='resource-requests-user'))

    def __config_database_and_security(self):
        db.init_app(self.app)
        self.__config_flask_security()
        db_utils.setup_development_data(self.app)

    def __config_flask_security(self):
        Security(self.app, user_datastore, register_form=ExtendedRegisterForm)

    def __config_blueprints(self):
        self.app.register_blueprint(default_blueprint)
