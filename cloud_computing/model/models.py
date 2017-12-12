# -*- coding: utf-8 -*-

from flask_security import RoleMixin, UserMixin
from sqlalchemy import func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import validates

from cloud_computing.model.database import db

# Create a table to support many-to-many relationship between Users and Roles
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    # Human-readable values for the Role when editing a User
    def __str__(self):
        return self.name

    # Required to avoid the exception TypeError: unhashable type:
    # 'Role' when saving a User
    def __hash__(self):
        return hash(self.name)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    cpf = db.Column(db.String(11))
    cnpj = db.Column(db.String(14))
    company = db.Column(db.Text)
    password = db.Column(db.Text, nullable=False)
    active = db.Column(db.Boolean(), server_default='true')
    confirmed_at = db.Column(db.DateTime(), server_default=func.now())

    roles = db.relationship(
        'Role',
        secondary=roles_users,
        backref=db.backref('users', lazy='dynamic')
    )

    def __str__(self):
        return self.email


class Plan(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.Text, unique=True)
    price = db.Column(db.Float(), nullable=False)
    description = db.Column(db.Text)
    period = db.Column(db.Integer, nullable=False)
    is_public = db.Column(db.Boolean, server_default='false')
    cpu_model = db.Column(db.Text, db.ForeignKey('cpu.model'), nullable=False)
    os_name = db.Column(db.Text, db.ForeignKey('os.name'), nullable=False)

    os = db.relationship('Os', backref=db.backref('plans'))
    cpu = db.relationship('Cpu', backref=db.backref('plans'))
    gpu = db.relationship('Gpu', secondary='plan_gpu')
    ram = db.relationship('Ram', secondary='plan_ram')
    hd = db.relationship('Hd', secondary='plan_hd')


class ResourceRequests(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    message = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message_date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    answer_date = db.Column(db.DateTime(timezone=True))

    admin_rel = db.relationship('User', foreign_keys=[admin_id])
    user_rel = db.relationship('User', foreign_keys=[user_id])


class Resource:
    """Base class of Cpu, Gpu, Ram, Hd. Declares common attributes and functions shared by this classes."""
    model = db.Column(db.Text, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    available = db.Column(db.Integer)

    @validates('total')
    def update_total(self, key, value):
        """On adding new components, update the available components."""
        if value < 0:
            raise ValueError("O valor não pode ser menor que zero.")
        elif self.total is None:
            self.available = value
        else:
            self.available = self.available + value-self.total
        return value

    def __str__(self):
        return self.model

    @validates('price')
    def check_price(self, key, value):
        if value < 0:
            raise ValueError("O preço não pode ser menor que zero.")
        else:
            return value


class Cpu(db.Model, Resource):
    cores = db.Column(db.Integer, nullable=False)
    frequency = db.Column(db.Float, nullable=False)


class Gpu(db.Model, Resource):
    frequency = db.Column(db.Float, nullable=False)
    ram = db.Column(db.Integer, nullable=False)


class Ram(db.Model, Resource):
    capacity = db.Column(db.Integer, nullable=False)


class Hd(db.Model, Resource):
    capacity = db.Column(db.Integer, nullable=False)
    is_ssd = db.Column(db.Boolean, server_default='false')


class Os(db.Model):
    name = db.Column(db.Text, primary_key=True)

    def __str__(self):
        return self.name


class PlanResource:
    """Base class of PlanGpu, PlanRam, PlanHd. Declares common attributes and functions shared by this classes."""
    backref_plan = 'plan_comps'
    quantity = db.Column(db.Integer)

    @declared_attr
    def plan_id(self):
        return db.Column(db.Integer, db.ForeignKey('plan.id'),
                         primary_key=True)

    @declared_attr
    def plans(self):
        return db.relationship('Plan', backref=db.backref(self.backref_plan))


class PlanGpu(db.Model, PlanResource):
    backref_plan = 'plan_gpus'

    gpu_model = db.Column(db.Text, db.ForeignKey('gpu.model'), primary_key=True)
    gpus = db.relationship('Gpu', backref=db.backref('plan_gpus'))


class PlanRam(db.Model, PlanResource):
    backref_plan = 'plan_rams'

    ram_model = db.Column(db.Text, db.ForeignKey('ram.model'), primary_key=True)
    rams = db.relationship('Ram', backref=db.backref('plan_rams'))


class PlanHd(db.Model, PlanResource):
    backref_plan = 'plan_hds'

    hd_model = db.Column(db.Text, db.ForeignKey('hd.model'), primary_key=True)
    hds = db.relationship('Hd', backref=db.backref('plan_hds'))


class CreditCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.BigInteger, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    exp_date = db.Column(db.DateTime, nullable=False)
    cvv = db.Column(db.Integer, nullable=False)

    users = db.relationship('User', backref=db.backref('credit_cards'))


class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    credit_card_id = db.Column(db.Integer, db.ForeignKey('credit_card.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=False)

    users = db.relationship('User', backref=db.backref('purchases'))
    credit_cards = db.relationship('CreditCard', backref=db.backref('purchases'))
    plans = db.relationship('Plan', backref=db.backref('purchases'))
