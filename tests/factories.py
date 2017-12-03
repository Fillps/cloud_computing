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


class PlanFactory(SQLAlchemyModelFactory):
    id = factory.Sequence(lambda x: x)
    title = factory.Sequence(lambda x: x)
    price = factory.Sequence(lambda x: x)
    description = factory.Sequence(lambda x: x)

    class Meta:
        model = models.Plan
        sqlalchemy_session = db.session