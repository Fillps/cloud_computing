# -*- coding: utf-8 -*-
from flask_security import utils

from cloud_computing.model.database import db, user_datastore, get_or_create, get
from cloud_computing.model.models import *


def setup_database(app):
    """Creates test data before the app runs, should not go to production."""

    # Create any database tables that don't exist yet
    with app.app_context():
        db.create_all()

        # Create the Roles "admin" and "end-user" -- unless they already exist
        user_datastore.find_or_create_role(name='admin',
                                           description='Administrator')
        user_datastore.find_or_create_role(name='end-user',
                                           description='End user')

        # Create two Users for testing purposes -- unless they already exists
        # In each case use Flask-Security utility function to encrypt the password
        encrypted_password = utils.hash_password('password')

        if user_datastore.find_user(id=1, email='someone@example.com') is None:
            user_datastore.create_user(id=1,
                                       name='someone',
                                       last_name='example',
                                       cpf='00099988877',
                                       email='someone@example.com',
                                       password=encrypted_password)

        if user_datastore.find_user(id=2, email='admin@example.com') is None:
            user_datastore.create_user(id=2,
                                       name='admin',
                                       last_name='example',
                                       cpf='00099988878',
                                       email='admin@example.com',
                                       password=encrypted_password)

        get_or_create(db.session, Os, name='Windows')
        get_or_create(db.session, Os, name='Linux')

        if get(db.session, Cpu, model="CPU 2 Cores 2.0") is None:
            get_or_create(db.session, Cpu,
                          model="CPU 2 Cores 2.0",
                          cores=2,
                          frequency=2.0,
                          price=3.99,
                          total=10)

        if get(db.session, Cpu, model="CPU 4 Cores 2.0") is None:
            get_or_create(db.session, Cpu,
                          model="CPU 4 Cores 2.0",
                          cores=4,
                          frequency=2.0,
                          price=5.99,
                          total=10)
        if get(db.session, Cpu, model="GPU 4GB 2.0") is None:
            get_or_create(db.session, Gpu,
                          model="GPU 4GB 2.0",
                          ram=4,
                          frequency=2.0,
                          price=3.99,
                          total=10)
        if get(db.session, Cpu, model="GPU 8GB 2.0") is None:
            get_or_create(db.session, Gpu,
                          model="GPU 8GB 2.0",
                          ram=8,
                          frequency=2.0,
                          price=5.99,
                          total=10)

        if get(db.session, Cpu, model="RAM 8GB") is None:
            get_or_create(db.session, Ram,
                          model="RAM 8GB",
                          capacity=8,
                          price=3.99,
                          total=10)
        if get(db.session, Cpu, model="RAM 4GB") is None:
            get_or_create(db.session, Ram,
                          model="RAM 4GB",
                          capacity=4,
                          price=2.99,
                          total=10)

        if get(db.session, Cpu, model="HD 100GB") is None:
            get_or_create(db.session, Hd,
                          model="HD 100GB",
                          capacity=100,
                          price=3.99,
                          total=10)

        if get(db.session, Cpu, model="HD 500GB") is None:
            get_or_create(db.session, Hd,
                          model="HD 500GB",
                          capacity=500,
                          price=5.99,
                          total=10)

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
        get_or_create(db.session, Plan,
                      title='Plano básico',
                      price=19.99,
                      description='Descrição do plano básico',
                      is_public=True,
                      cpu_model='CPU 2 Cores 2.0',
                      os_name='Linux')

        get_or_create(db.session, Plan,
                      title='Plano intermediário',
                      price=29.99,
                      description='Descrição do plano intermediário',
                      is_public=True,
                      cpu_model='CPU 4 Cores 2.0',
                      os_name='Linux')

        get_or_create(db.session, Plan,
                      title='Plano avançado',
                      price=39.99,
                      description='Descrição do plano avançado',
                      is_public=True,
                      cpu_model='CPU 4 Cores 2.0',
                      os_name='Linux')

        # Commit changes
        db.session.commit()
