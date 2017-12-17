# -*- coding: utf-8 -*-

from slugify import slugify
from flask_security import RoleMixin, UserMixin
from sqlalchemy import func, event
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import validates
from wtforms import ValidationError

from cloud_computing.model.database import db
from cloud_computing.utils.db_utils import get

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
    duration_months = db.Column(db.Integer, nullable=False)
    cpu_model = db.Column(db.Text, db.ForeignKey('cpu.model'), nullable=False)
    os_name = db.Column(db.Text, db.ForeignKey('os.name'), nullable=False)
    shop_description = db.Column(db.Text)
    slug_url = db.Column(db.Text, unique=True)
    thumbnail = db.Column(db.Text, default='http://placehold.it/700x400')
    hero_image = db.Column(db.Text, default='http://placehold.it/900x400')
    is_public = db.Column(db.Boolean, default='false')

    os = db.relationship('Os', backref=db.backref('plans'))
    cpu = db.relationship('Cpu', backref=db.backref('plans'))
    gpu = db.relationship('Gpu', secondary='plan_gpu')
    ram = db.relationship('Ram', secondary='plan_ram')
    hd = db.relationship('Hd', secondary='plan_hd')

    @validates('title')
    def update_slug(self, key, value):
        """Creates the slug url, used on the item detail page."""
        self.slug_url = slugify(value)
        return value


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
    model = db.Column(db.Text, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    available = db.Column(db.Integer)

    @validates('total')
    def update_total(self, key, value):
        """On adding new components, update the available components."""
        if value < 0:
            raise ValidationError("O valor não pode ser menor que zero.")
        elif self.total is None:
            self.available = value
        else:
            self.available += value - self.total
        return value

    def __str__(self):
        return self.model

    @validates('price')
    def check_price(self, key, value):
        if value < 0:
            raise ValidationError("O preço não pode ser menor que zero.")
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


class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpu_model = db.Column(db.Text, db.ForeignKey('cpu.model'), nullable=False)
    cores_available = db.Column(db.Integer, default=0)
    os_name = db.Column(db.Text, db.ForeignKey('os.name'))
    ram_slot_total = db.Column(db.Integer, nullable=False)
    ram_slot_available = db.Column(db.Integer)
    ram_max = db.Column(db.Integer, nullable=False)
    ram_total = db.Column(db.Integer, default=0)
    ram_available = db.Column(db.Integer, default=0)
    gpu_slot_total = db.Column(db.Integer, nullable=False)
    gpu_slot_available = db.Column(db.Integer)
    gpu_total = db.Column(db.Integer, default=0)
    gpu_available = db.Column(db.Integer, default=0)
    hd_slot_total = db.Column(db.Integer, nullable=False)
    hd_slot_available = db.Column(db.Integer)
    hd_total = db.Column(db.Integer, default=0)
    hd_available = db.Column(db.Integer, default=0)
    ssd_total = db.Column(db.Integer, default=0)
    ssd_available = db.Column(db.Integer, default=0)

    os = db.relationship('Os', backref=db.backref('server'))
    cpu = db.relationship('Cpu', backref=db.backref('server'))
    gpus = db.relationship('Gpu', secondary='server_gpu')
    rams = db.relationship('Ram', secondary='server_ram')
    hds = db.relationship('Hd', secondary='server_hd')

    @validates('cpu_model')
    def cpu_model_update(self, key, value):
        """Update the cores_available when the cpu_model updates."""
        new_cpu = get(db.session, Cpu, model=value)
        if self.cpu_model is None:
            cores_available = new_cpu.cores
        elif self.cpu.available < 1:
            raise ValidationError("Não existe CPU disponível.")
        else:
            cores_available = new_cpu.cores + self.cores_available - self.cpu.cores
        if cores_available < 0:
            if key != -1:
                raise ValidationError("O uso de cores está maior do que o disponível. "
                                      "Tente diminuir a utilização de cores ou aumente "
                                      "os cores do cpu a ser adicionado.")
        else:
            self.cores_available = cores_available
            new_cpu.available -= 1
            return value

    @validates('ram_slot_total', 'gpu_slot_total', 'hd_slot_total')
    def update_ram_slot_total(self, key, value):
        available = key[:-5] + 'available'
        available_value = self.__getattribute__(available)
        old_value = self.__getattribute__(key)
        if available_value is None:
            self.__setattr__(available, value)
        elif available_value + value - old_value < 0:
            raise ValidationError("Falha ao remover os slots. Tente remover os componentes antes.")
        else:
            self.__setattr__(available, available_value + value - old_value)
        return value


class ServerResource:
    backref_plan = 'server_resources'
    quantity = db.Column(db.Integer, default=0)

    @declared_attr
    def server_id(self):
        return db.Column(db.Integer, db.ForeignKey('server.id'), primary_key=True)

    @declared_attr
    def server(self):
        return db.relationship('Server', backref=db.backref(self.backref_plan))


class ServerGpu(db.Model, ServerResource):
    backref_plan = 'server_gpus'
    gpu_model = db.Column(db.Text, db.ForeignKey('gpu.model'), primary_key=True)
    total_capacity = db.Column(db.Integer, default=0)
    available_capacity = db.Column(db.Integer, default=0)

    gpu = db.relationship('Gpu', backref=db.backref(backref_plan))

    @validates('quantity')
    def update_quantity(self, key, value):
        """
            When quantity is updated, updates the total_capacity, available_capacity, gpu.available
            and server.gpu_slot_available.
        """
        if value < 0:
            raise ValidationError('A quantidade precisa ser maior que zero.')
        elif self.server_id is None:
            return value
        elif self.gpu.available < value - self.quantity:
            raise ValidationError(
                "Não existem recursos disponíveis. Tente diminuir a quantidade ou adicionar novos recursos.")
        elif self.server.gpu_slot_available < value - self.quantity:
            raise ValidationError(
                "Não existem slots disponíveis. Tente diminuir a quantidade de recursos.")

        net_capacity = self.gpu.ram * value - self.gpu.ram * self.quantity

        if self.available_capacity + net_capacity < 0:
            raise ValidationError(
                "O uso do recurso está maior do que o disponível. Tente diminuir a utilização dos recursos"
                " ou aumente a quantidade de recursos a serem adicionados.")
        else:
            self.total_capacity += net_capacity
            self.available_capacity += net_capacity
            self.gpu.available -= value - self.quantity
            self.server.gpu_slot_available -= value - self.quantity
            return value


@event.listens_for(ServerGpu, 'before_insert')
def server_gpu_before_insert(maper, connection, target):
    """Before the insert, updates the total_capacity, available_capacity,
    gpu.available and server.gpu_slot_available based on the quantity.
    """
    if target.gpu.available < target.quantity:
        raise ValidationError("Não existem recursos disponíveis. Tente diminuir "
                              "a quantidade ou adicionar novos recursos.")
    elif target.server.gpu_slot_available < target.quantity:
        raise ValidationError("Não existem slots no servidor disponíveis."
                              "Tente diminuir a quantidade.")
    else:
        target.available_capacity = target.gpu.ram * target.quantity
        target.total_capacity = target.gpu.ram * target.quantity
        connection.execute(Server.__table__.update()
                           .where(Server.__table__.c.id == target.server_id)
                           .values(gpu_slot_available=target.server.gpu_slot_available - target.quantity))
        connection.execute(Gpu.__table__.update()
                           .where(Gpu.__table__.c.model == target.gpu_model)
                           .values(available=target.gpu.available - target.quantity))


@event.listens_for(ServerGpu, 'before_delete')
def server_gpu_before_delete(maper, connection, target):
    """ Before the delete, updates the gpu.available and
    server.gpu_slot_available based on the quantity.
    """
    if target.available_capacity < target.total_capacity:
        raise ValidationError('Erro! O GPU a ser deletado ainda está em uso!')
    else:
        connection.execute(Server.__table__.update()
                           .where(Server.__table__.c.id == target.server_id)
                           .values(gpu_slot_available=target.server.ram_slots_available + target.quantity))
        connection.execute(Gpu.__table__.update()
                           .where(Gpu.__table__.c.model == target.gpu_model)
                           .values(available=target.gpu.available + target.quantity))


class ServerRam(db.Model, ServerResource):
    backref_plan = 'server_rams'
    ram_model = db.Column(db.Text, db.ForeignKey('ram.model'), primary_key=True)
    ram = db.relationship('Ram', backref=db.backref(backref_plan))

    @validates('quantity')
    def update_quantity(self, key, value):
        """When quantity is updated, updates the server.ram_total,
        server.ram_available, ram.available and server.ram_slot_available.
        """
        if value < 0:
            raise ValidationError('A quantidade precisa ser maior que zero.')
        elif self.server_id is None:
            return value
        elif self.ram.available < value - self.quantity:
            raise ValidationError(
                "Não existem recursos disponíveis. Tente diminuir a quantidade ou adicionar novos recursos.")
        elif self.server.ram_slot_available < value - self.quantity:
            raise ValidationError(
                "Não existem slots disponíveis. Tente diminuir a quantidade de recursos.")

        net_capacity = self.ram.capacity * value - self.ram.capacity * self.quantity

        if self.server.ram_available + net_capacity < 0:
            raise ValidationError("O uso do recurso está maior do que o disponível. "
                                  "Tente diminuir a utilização dos recursos ou aumente "
                                  "a quantidade de recursos a serem adicionados.")
        elif self.server.ram_max < self.server.ram_total + net_capacity:
            raise ValidationError("RAM máxima do servidor atingida.")
        else:
            self.server.ram_total += net_capacity
            self.server.ram_available += net_capacity
            self.server.ram_slot_available -= value - self.quantity
            self.ram.available -= value - self.quantity
            return value


@event.listens_for(ServerRam, 'before_insert')
def server_ram_before_insert(maper, connection, target):
    """ Before the insert, updates the server.ram_total, server.ram_available,
    ram.available and server.ram_slot_available based on the quantity.
    """
    if target.ram.available < target.quantity:
        raise ValidationError("Não existem recursos disponíveis. Tente diminuir "
                              "a quantidade ou adicionar novos recursos.")
    elif target.server.ram_slot_available < target.quantity:
        raise ValidationError("Não existem slots no servidor disponíveis."
                              "Tente diminuir a quantidade.")
    elif target.server.ram_max < target.server.ram_total + target.ram.capacity * target.quantity:
        raise ValidationError("RAM máxima do servidor atingida.")
    else:
        added_capacity = target.ram.capacity * target.quantity
        connection.execute(Server.__table__.update()
                           .where(Server.__table__.c.id == target.server_id)
                           .values(ram_total=target.server.ram_total + added_capacity,
                                   ram_available=target.server.ram_available + added_capacity,
                                   ram_slot_available=target.server.ram_slot_available - target.quantity))
        connection.execute(Ram.__table__.update()
                           .where(Ram.__table__.c.model == target.ram_model)
                           .values(available=target.ram.available - target.quantity))


@event.listens_for(ServerRam, 'before_delete')
def server_ram_before_delete(maper, connection, target):
    """ Before the delete, updates the server.ram_total, server.ram_available,
    ram.available and server.ram_slot_available based on the quantity.
    """
    if target.quantity * target.ram.capacity > target.server.ram_available:
        raise ValidationError('Erro! A RAM a ser deletada ainda está em uso!')
    else:
        removed_capacity = target.quantity * target.ram.capacity
        connection.execute(Server.__table__.update()
                           .where(Server.__table__.c.id == target.server_id)
                           .values(ram_total=target.server.ram_total - removed_capacity,
                                   ram_available=target.server.ram_available - removed_capacity,
                                   ram_slot_available=target.server.ram_slot_available + target.quantity))
        connection.execute(Ram.__table__.update()
                           .where(Ram.__table__.c.model == target.ram_model)
                           .values(available=target.ram.available + target.quantity))


class ServerHd(db.Model, ServerResource):
    backref_plan = 'server_hds'
    hd_model = db.Column(db.Text, db.ForeignKey('hd.model'), primary_key=True)
    hd = db.relationship('Hd', backref=db.backref(backref_plan))

    @validates('quantity')
    def update_quantity(self, key, value):
        """ When quantity is updated, updates the server.hd_total,
        server.hd_available, server.ssd_total, server.ssd_available,
        hd.available and server.hd_slot_available.
        """
        if value < 0:
            raise ValidationError('A quantidade precisa ser maior que zero.')
        elif self.server_id is None:
            return value
        elif self.hd.available < value - self.quantity:
            raise ValidationError(
                "Não existem recursos disponíveis. Tente diminuir a quantidade ou adicionar novos recursos.")
        elif self.server.hd_slot_available < value - self.quantity:
            raise ValidationError(
                "Não existem slots disponíveis. Tente diminuir a quantidade de recursos.")

        net_capacity = self.hd.capacity * value - self.hd.capacity * self.quantity

        if (self.hd.is_ssd is True and self.server.ssd_available + net_capacity < 0) or \
                (self.hd.is_ssd is False and self.server.hd_available + net_capacity < 0):
            raise ValidationError(
                "O uso do recurso está maior do que o disponível. Tente diminuir a utilização dos recursos"
                " ou aumente a quantidade de recursos a serem adicionados.")
        else:
            if self.hd.is_ssd is True:
                self.server.ssd_total += net_capacity
                self.server.ssd_available += net_capacity
            else:
                self.server.hd_total += net_capacity
                self.server.hd_available += net_capacity
            self.hd.available -= value - self.quantity
            self.server.hd_slot_available -= value - self.quantity
            return value


@event.listens_for(ServerHd, 'before_insert')
def server_hd_before_insert(maper, connection, target):
    """Before the insert, updates the server.hd_total, server.hd_available,
    server.ssd_total, server.ssd_available, hd.available and
    server.hd_slot_available based on the quantity.
    """
    if target.hd.available < target.quantity:
        raise ValidationError("Não existem recursos disponíveis. Tente diminuir "
                              "a quantidade ou adicionar novos recursos.")
    elif target.server.hd_slot_available < target.quantity:
        raise ValidationError("Não existem slots no servidor disponíveis."
                              "Tente diminuir a quantidade.")
    else:
        added_capacity = target.hd.capacity * target.quantity
        if target.hd.is_ssd is True:
            server_values = {'ssd_available': target.server.ssd_available + added_capacity,
                             'ssd_total': target.server.ssd_available + added_capacity}
        else:
            server_values = {'hd_available': target.server.hd_available + added_capacity,
                             'hd_total': target.server.hd_available + added_capacity}
        connection.execute(Server.__table__.update()
                           .where(Server.__table__.c.id == target.server_id)
                           .values(**server_values,
                                   hd_slot_available=target.server.hd_slot_available - target.quantity))
        connection.execute(Hd.__table__.update()
                           .where(Hd.__table__.c.model == target.hd_model)
                           .values(available=target.hd.available - target.quantity))


@event.listens_for(ServerHd, 'before_delete')
def server_hd_before_delete(maper, connection, target):
    """Before the delete, updates the server.hd_total, server.hd_available,
    server.ssd_total, server.ssd_available, hd.available and
    server.hd_slot_available based on the quantity.
    """
    if target.quantity * target.hd.capacity > target.server.hd_available:
        raise ValidationError('Erro! O HD a ser deletado ainda está em uso!')
    else:
        removed_capacity = target.quantity * target.hd.capacity
        if target.hd.is_ssd is True:
            server_values = {'ssd_available': target.server.ssd_available - removed_capacity,
                             'ssd_total': target.server.ssd_available - removed_capacity}
        else:
            server_values = {'hd_available': target.server.hd_available - removed_capacity,
                             'hd_total': target.server.hd_available - removed_capacity}

        connection.execute(Server.__table__.update()
                           .where(Server.__table__.c.id == target.server_id)
                           .values(**server_values,
                                   hd_slot_available=target.server.hd_slot_available + target.quantity))
        connection.execute(Hd.__table__.update()
                           .where(Hd.__table__.c.model == target.hd_model)
                           .values(available=target.hd.available + target.quantity))
