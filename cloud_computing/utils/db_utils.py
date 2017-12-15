# -*- coding: utf-8 -*-

import datetime
from flask_security import utils


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


END_USER_ID = 1500
ADMIN_ID = 1501


def setup_development_data(app):
    """Creates test data before the app runs, should not go to production."""

    from cloud_computing.model.database import db
    from cloud_computing.model.models import Os, Cpu, Gpu, Ram, Hd, ResourceRequests, CreditCard, Server, Plan
    from cloud_computing.model.database import user_datastore

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

        if user_datastore.find_user(id=END_USER_ID, email='someone@example.com') is None:
            user_datastore.create_user(id=END_USER_ID,
                                       name='someone',
                                       last_name='example',
                                       cpf='00099988877',
                                       email='someone@example.com',
                                       password=encrypted_password)

        if user_datastore.find_user(id=ADMIN_ID, email='admin@example.com') is None:
            user_datastore.create_user(id=ADMIN_ID,
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
                      user_id=END_USER_ID)
        get_or_create(db.session, ResourceRequests, message='Teste de requisição de recurso 2',
                      user_id=END_USER_ID)

        # Set example users roles
        user_datastore.add_role_to_user('someone@example.com', 'end-user')
        user_datastore.add_role_to_user('admin@example.com', 'admin')

        # Create a credit card for user 1
        get_or_create(db.session, CreditCard,
                      user_id=END_USER_ID,
                      number=9999999999999999,
                      name='SOMEONE CARD',
                      cvv=123,
                      exp_date=datetime.datetime(day=1, month=6, year=2030))

        db.session.commit()

        # Create first test plans if they don't exist
        get_or_create(db.session, Plan,
                      title='Plano básico',
                      price=19.99,
                      shop_description='Descrição do plano básico',
                      period=1,
                      is_public=True,
                      cpu_model='CPU 2 Cores 2.0',
                      os_name='Linux',
                      hero_image="https://i.imgur.com/ZVunLlo.png",
                      thumbnail="https://i.imgur.com/IBxTPUs.jpg")

        get_or_create(db.session, Plan,
                      title='Plano intermediário',
                      price=29.99,
                      shop_description='Descrição do plano intermediário',
                      period=1,
                      is_public=True,
                      cpu_model='CPU 4 Cores 2.0',
                      os_name='Linux',
                      hero_image="https://i.imgur.com/jMpKAaJ.png",
                      thumbnail="https://i.imgur.com/gT83VXZ.jpg")

        get_or_create(db.session, Plan,
                      title='Plano avançado',
                      price=39.99,
                      shop_description='Descrição do plano avançado',
                      period=1,
                      is_public=True,
                      cpu_model='CPU 4 Cores 2.0',
                      os_name='Linux',
                      hero_image="https://i.imgur.com/jXdehmz.jpg",
                      thumbnail="https://i.imgur.com/YJChIXK.jpg")

        if get(db.session, Server, id=1500) is None:
            get_or_create(db.session, Server,
                          id=1500,
                          cpu_model='CPU 4 Cores 2.0',
                          ram_slot_total=10,
                          ram_max=160,
                          gpu_slot_total=10,
                          hd_slot_total=100,
                          os_name='Linux')
        # Commit changes
        db.session.commit()
