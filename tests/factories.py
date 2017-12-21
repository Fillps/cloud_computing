# -*- coding: utf-8 -*-

import datetime
import factory
from factory import lazy_attribute
from factory.alchemy import SQLAlchemyModelFactory

from cloud_computing.model import models
from cloud_computing.model.database import db


class RoleFactory(SQLAlchemyModelFactory):
    id = factory.Sequence(lambda x: x)
    name = factory.Sequence(lambda x: x)
    description = factory.Sequence(lambda x: x)


class UserFactory(SQLAlchemyModelFactory):
    id = factory.Sequence(lambda x: x)
    name = factory.Sequence(lambda x: x)
    last_name = factory.Sequence(lambda x: x)
    email = lazy_attribute(lambda x: str(x.id) + "@example.com")
    cpf = None
    cnpj = None
    company = None
    password = factory.Sequence(lambda x: x)
    active = True
    confirmed_at = datetime.datetime.now()

    @factory.post_generation
    def roles(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for role in extracted:
                self.roles.add(role)

    class Meta:
        model = models.User
        sqlalchemy_session = db.session


class CpuFactory(SQLAlchemyModelFactory):
    model = factory.Sequence(lambda x: x)
    cores = 4
    frequency = 2.0
    price = 5.99
    total = 10

    class Meta:
        model = models.Cpu
        abstract = False


class GpuFactory(SQLAlchemyModelFactory):
    model = factory.Sequence(lambda x: x)
    frequency = 2.0
    ram = 4
    price = 3.99
    total = 10

    class Meta:
        model = models.Gpu


class RamFactory(SQLAlchemyModelFactory):
    model = factory.Sequence(lambda x: str(x))
    capacity = 4
    price = 3.99
    total = 10

    class Meta:
        model = models.Ram


class HdFactory(SQLAlchemyModelFactory):
    model = factory.Sequence(lambda x: x)
    capacity = 100
    price = 3.99
    total = 10

    class Meta:
        model = models.Hd


class OsFactory(SQLAlchemyModelFactory):
    name = factory.Sequence(lambda x: x)

    class Meta:
        model = models.Os


class PlanFactory(SQLAlchemyModelFactory):
    id = factory.Sequence(lambda x: x)
    title = factory.Sequence(lambda x: str(x))
    price = factory.Sequence(lambda x: x)
    duration_months = factory.Sequence(lambda x: x)
    cpu = factory.SubFactory(CpuFactory, model=factory.Sequence(lambda x: str(x)))
    os = factory.SubFactory(OsFactory)
    shop_description = factory.Sequence(lambda x: str(x))

    class Meta:
        model = models.Plan
        sqlalchemy_session = db.session


class ServerFactory(SQLAlchemyModelFactory):
    id = factory.Sequence(lambda x: x)
    cpu = factory.SubFactory(CpuFactory, model=factory.Sequence(lambda x: str(x)))
    ram_slot_total = 10
    ram_max = 160
    gpu_slot_total = 10
    hd_slot_total = 100

    class Meta:
        model = models.Server


class ServerRamFactory(SQLAlchemyModelFactory):
    ram = factory.SubFactory(RamFactory)
    server = factory.SubFactory(ServerFactory)
    quantity = factory.Sequence(lambda x: x)

    class Meta:
        model = models.ServerRam


class CreditCardFactory(SQLAlchemyModelFactory):
    id = factory.Sequence(lambda x: x)
    number = factory.Sequence(lambda x: x)
    user = factory.SubFactory(UserFactory, id=1500)
    name = factory.Sequence(lambda x: x)
    exp_date = factory.Sequence(lambda x: x)
    cvv = factory.Sequence(lambda x: x)

    class Meta:
        model = models.CreditCard


class PurchaseFactory(SQLAlchemyModelFactory):
    id = factory.Sequence(lambda x: x)
    user = factory.SubFactory(UserFactory)
    credit_card = factory.SubFactory(CreditCardFactory)
    plan = factory.SubFactory(PlanFactory)

    class Meta:
        model = models.Purchase


