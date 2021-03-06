# -*- coding: utf-8 -*-

import datetime
from slugify import slugify
from wtforms import ValidationError
from flask_security import RoleMixin, UserMixin
from sqlalchemy import func, event
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import validates, Session

from cloud_computing.model.database import db
from cloud_computing.utils.form_utils import add_months

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
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, unique=True, default='Customizado')
    price = db.Column(db.Float(), default=0, nullable=False)
    duration_months = db.Column(db.Integer, nullable=False)
    cpu_model = db.Column(db.Text, db.ForeignKey('cpu.model'), nullable=False)
    os_name = db.Column(db.Text, db.ForeignKey('os.name'), nullable=False)
    shop_description = db.Column(db.Text)
    slug_url = db.Column(db.Text, unique=True)
    thumbnail = db.Column(db.Text, default='http://placehold.it/700x400')
    hero_image = db.Column(db.Text, default='http://placehold.it/900x400')
    is_public = db.Column(db.Boolean, default='false')
    auto_price = db.Column(db.Boolean, default=True)

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

    def __str__(self):
        return self.title

    @validates('auto_price')
    def auto_price_update(self, key, value):
        if value is True:
            self.price = -1
        return value

    @validates('price')
    def price_update(self, key, value):
        if self.auto_price is True:
            if self.cpu_model is not None:
                return self.calculate_price()
        return value

    @validates('cpu')
    def cpu_update(self, key, value):
        if self.auto_price is True:
            self.price = -1
        return value

    def calculate_price(self):
        price = Cpu.query.filter_by(model=self.cpu_model).first().price * self.duration_months
        for plan_hd in PlanHd.query.filter_by(plan_id=self.id):
            price += plan_hd.quantity * plan_hd.hd.price * self.duration_months
        for plan_ram in PlanRam.query.filter_by(plan_id=self.id):
            price += plan_ram.quantity * plan_ram.ram.price * self.duration_months
        for plan_gpu in PlanGpu.query.filter_by(plan_id=self.id):
            price += plan_gpu.quantity * plan_gpu.gpu.price * self.duration_months
        return price

    def get_total_ram(self):
        total_ram = 0
        for ram in self.plan_rams:
            total_ram += ram.quantity * ram.ram.capacity
        return total_ram

    def get_total_hd_ssd(self):
        total_hd = 0
        total_ssd = 0
        for hd in self.plan_hds:
            if hd.hd.is_ssd is True:
                total_ssd += hd.quantity * hd.hd.capacity
            else:
                total_hd += hd.quantity * hd.hd.capacity
        return total_hd, total_ssd

    def available_servers(self, only_one=False, server_id=None):
        """
        :param only_one: when True finds only one server.
        :param server_id: search only the specified server
        :return: when only_one is True returns the server found and the used
                        resources(used_gpus, total_ram, total_hd, total_ssd)
                when only_one is False returns a list of available servers
                when there is no server available, returns None.
        """
        total_ram = self.get_total_ram()

        total_hd, total_ssd = self.get_total_hd_ssd()

        if server_id is None:
            servers = Server.query.filter(Server.cores_available >= self.cpu.cores,
                                          Server.ram_available >= total_ram,
                                          Server.hd_available >= total_hd,
                                          Server.ssd_available >= total_ssd,
                                          Server.os_name == self.os_name)
        else:
            servers = Server.query.filter(Server.cores_available >= self.cpu.cores,
                                          Server.ram_available >= total_ram,
                                          Server.hd_available >= total_hd,
                                          Server.ssd_available >= total_ssd,
                                          Server.os_name == self.os_name,
                                          Server.id == server_id)
        available_servers = []
        # percorre todos os servidores
        for server in servers:
            plan_gpus = list(self.plan_gpus)
            used_gpus = {}
            # percorre todas as GPUs do servidor
            for server_gpu in server.server_gpus:
                # percorre todas as GPUs do plano
                for plan_gpu in self.plan_gpus:
                    # verifica se a GPU ja foi usada antes, se não coloca o valor da utiliazaão dela pra zero
                    if server_gpu.gpu_model not in used_gpus:
                        used_gpus[server_gpu.gpu_model] = 0
                    # testa se a freq é a mesma e a capacidade é maior ou igual,
                    # levando em consideração se a gpu já foi usada antes
                    if server_gpu.gpu.frequency == plan_gpu.gpu.frequency and \
                                    server_gpu.available_capacity >= plan_gpu.quantity * plan_gpu.gpu.ram + used_gpus[
                                server_gpu.gpu_model]:
                        # remove a gpu da lista para nao passar na proxima gpu do servidor
                        plan_gpus.remove(plan_gpu)
                        # incrementa a utilização da gpu do servidor
                        used_gpus[server_gpu.gpu_model] += plan_gpu.quantity * plan_gpu.gpu.ram
            if len(plan_gpus) == 0 and only_one is True:
                return server, used_gpus, total_ram, total_hd, total_ssd
            elif len(plan_gpus) == 0:
                available_servers.append(server)
        if len(available_servers) == 0:
            return None
        return available_servers


@event.listens_for(Plan, 'after_insert')
def plan_after_insert(maper, connection, target):
    values = {}
    if target.title == 'Customizado':
        values['title'] = 'Customizado-' + str(target.id)
    if target.auto_price is True:
        values['price'] = target.calculate_price()
    if values:
        connection.execute(Plan.__table__.update()
                           .where(Plan.__table__.c.id == target.id)
                           .values(**values))


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
    quantity = db.Column(db.Integer, default=1)

    @declared_attr
    def plan_id(self):
        return db.Column(db.Integer, db.ForeignKey('plan.id'),
                         primary_key=True)

    @declared_attr
    def plan(self):
        return db.relationship('Plan', backref=db.backref(self.backref_plan))

    @validates('quantity')
    def quantity_update(self, key, value):
        if self.plan.auto_price is True:
            self.plan.price = -1
        return value


class PlanGpu(db.Model, PlanResource):
    backref_plan = 'plan_gpus'

    gpu_model = db.Column(db.Text, db.ForeignKey('gpu.model'), primary_key=True)
    gpu = db.relationship('Gpu', backref=db.backref('plan_gpu'))

    def __str__(self):
        return self.gpu.model + ' x ' + str(self.quantity)

    @validates('gpu')
    def update_gpu(self, key, value):
        if self.gpu is None or self.gpu == value:
            return value
        raise ValidationError("Não é possível alterar o modelo da GPU. "
                              "Delete esse componente e crie outro.")


class PlanRam(db.Model, PlanResource):
    backref_plan = 'plan_rams'

    ram_model = db.Column(db.Text, db.ForeignKey('ram.model'), primary_key=True)
    ram = db.relationship('Ram', backref=db.backref('plan_ram'))

    def __str__(self):
        return self.ram.model + ' x ' + str(self.quantity)

    @validates('ram')
    def update_ram(self, key, value):
        if self.ram is None or self.ram == value:
            return value
        raise ValidationError("Não é possível alterar o modelo da RAM. "
                              "Delete esse componente e crie outro.")


class PlanHd(db.Model, PlanResource):
    backref_plan = 'plan_hds'

    hd_model = db.Column(db.Text, db.ForeignKey('hd.model'), primary_key=True)
    hd = db.relationship('Hd', backref=db.backref('plan_hd'))

    def __str__(self):
        return self.hd.model + ' x ' + str(self.quantity)

    @validates('hd')
    def update_hd(self, key, value):
        if self.hd is None or self.hd == value:
            return value
        raise ValidationError("Não é possível alterar o modelo do HD. "
                              "Delete esse componente e crie outro.")


@event.listens_for(PlanGpu, 'after_insert')
def gpu_plan_after_insert(maper, connection, target):
    if target.plan.auto_price is True:
        connection.execute(Plan.__table__.update()
                           .where(Plan.__table__.c.id == target.plan_id)
                           .values(price=target.plan.calculate_price()))


@event.listens_for(PlanRam, 'after_insert')
def ram_plan_after_insert(maper, connection, target):
    if target.plan.auto_price is True:
        connection.execute(Plan.__table__.update()
                           .where(Plan.__table__.c.id == target.plan_id)
                           .values(price=target.plan.calculate_price()))


@event.listens_for(PlanHd, 'after_insert')
def hd_plan_after_insert(maper, connection, target):
    if target.plan.auto_price is True:
        connection.execute(Plan.__table__.update()
                           .where(Plan.__table__.c.id == target.plan_id)
                           .values(price=target.plan.calculate_price()))


class CreditCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.BigInteger, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    exp_date = db.Column(db.DateTime, nullable=False)
    cvv = db.Column(db.Integer, nullable=False)

    users = db.relationship('User', backref=db.backref('credit_cards'))

    def __str__(self):
        number_str = repr(self.number)
        return '****' + number_str[len(number_str) - 4:]


class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    credit_card_id = db.Column(db.Integer, db.ForeignKey('credit_card.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=False)
    user_plan_id = db.Column(db.Integer, db.ForeignKey('user_plan.id'))
    date = db.Column(db.DateTime, server_default=func.now())

    user = db.relationship('User', backref=db.backref('purchase'))
    credit_card = db.relationship('CreditCard', backref=db.backref('purchase'))
    plan = db.relationship('Plan', backref=db.backref('purchase'), )
    user_plan = db.relationship('UserPlan', backref=db.backref('purchases'), foreign_keys=[user_plan_id])


@event.listens_for(Purchase, 'after_insert')
def purchase_after_insert(maper, connection, target):
    """Creates or updates a UserPlan and updates the end_date by the plan duration_months.
        If is a new UserPlan, finds a server compatible with the plan and set the server in use."""

    @event.listens_for(Session, "after_flush", once=True)
    def receive_after_flush(session, context):

        if target.user_plan_id is None:
            plan = Plan.query.filter_by(id=target.plan_id).first()
            available_server = plan.available_servers(only_one=True)
            if available_server is None:
                raise ValidationError("Não existe servidor disponível para este plano. Mande um pedido "
                                      "de recurso para os administradores ou compre outro plano")

            server, used_gpus, total_ram, total_hd, total_ssd = available_server
            connection.execute(Server.__table__.update()
                               .where(Server.__table__.c.id == server.id)
                               .values(cores_available=server.cores_available - plan.cpu.cores,
                                       ram_available=server.ram_available - total_ram,
                                       hd_available=server.hd_available - total_hd,
                                       ssd_available=server.ssd_available - total_ssd))
            for gpu in server.server_gpus:
                if gpu.gpu_model in used_gpus and used_gpus[gpu.gpu_model] > 0:
                    connection.execute(ServerGpu.__table__.update()
                                       .where(ServerGpu.__table__.c.server_id == server.id and
                                              ServerGpu.__table__.c.gpu_model == gpu.gpu_model)
                                       .values(available_capacity=gpu.available_capacity - used_gpus[gpu.gpu_model]))

            user_plan = UserPlan(user_id=target.user_id,
                                 plan_id=target.plan_id,
                                 server_id=server.id)
            user_plan.end_date = add_months(datetime.datetime.now(), target.plan.duration_months)
            user_plan.purchases.append(target)
            session.add(user_plan)
        else:
            connection.execute(UserPlan.__table__.update()
                               .where(UserPlan.__table__.c.id == target.user_plan_id)
                               .values(end_date=add_months(target.user_plan.end_date, target.plan.duration_months)))


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
        new_cpu = Cpu.query.filter_by(model=value).first()
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

    @validates('user_plans')
    def user_plans_update(self, key, value):
        """When a user_plan is updated(server_id is changed),
           set all plan resources in use."""
        usage = value.plan.available_servers(only_one=True, server_id=self.id)
        if usage is None:
            raise ValidationError("Esse servidor não é compativel com esse plano.")
        server, used_gpus, total_ram, total_hd, total_ssd = usage

        self.cores_available -= value.plan.cpu.cores
        self.ram_available -= total_ram
        self.hd_available -= total_hd
        self.ssd_available -= total_ssd

        for gpu in self.server_gpus:
            if gpu.gpu_model in used_gpus and used_gpus[gpu.gpu_model] > 0:
                gpu.available_capacity -= used_gpus[gpu.gpu_model]
        return value


@event.listens_for(Server, 'before_insert')
def server_before_insert(maper, connection, target):
    """Initialize the available slots equal to total_slots."""
    target.ram_slot_available = target.ram_slot_total
    target.gpu_slot_available = target.gpu_slot_total
    target.hd_slot_available = target.hd_slot_total


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

    def __str__(self):
        return '%s x%s(%s/%s)' % (self.gpu.model, self.quantity, self.available_capacity, self.total_capacity)

    @validates('gpu')
    def update_gpu(self, key, value):
        if self.gpu is None or self.gpu == value:
            return value
        raise ValidationError("Não é possível alterar o modelo da GPU. "
                              "Delete esse componente e crie outro.")

    @validates('quantity')
    def update_quantity(self, key, value):
        """
            When quantity is updated, updates the total_capacity, available_capacity, gpu.available
            and server.gpu_slot_available.
        """
        if value < 0:
            raise ValidationError('A quantidade precisa ser maior que zero.')
        elif self.quantity is None:
            return value
        elif self.gpu.available < value - self.quantity:
            raise ValidationError(
                "Não existem recursos disponíveis. Tente diminuir a quantidade ou adicionar novos recursos.")
        elif self.server.gpu_slot_available < value - self.quantity:
            raise ValidationError(
                "Não existem slots disponíveis. Tente diminuir a quantidade de recursos.")

        net_capacity = self.gpu.ram * (value - self.quantity)

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
                           .values(gpu_slot_available=target.server.ram_slot_available + target.quantity))
        connection.execute(Gpu.__table__.update()
                           .where(Gpu.__table__.c.model == target.gpu_model)
                           .values(available=target.gpu.available + target.quantity))


class ServerRam(db.Model, ServerResource):
    backref_plan = 'server_rams'
    ram_model = db.Column(db.Text, db.ForeignKey('ram.model'), primary_key=True)
    ram = db.relationship('Ram', backref=db.backref(backref_plan))

    def __str__(self):
        return self.ram.model + ' x ' + str(self.quantity)

    @validates('ram')
    def update_ram(self, key, value):
        if self.ram is None or self.ram == value:
            return value
        raise ValidationError("Não é possível alterar o modelo da RAM. "
                              "Delete esse componente e crie outro.")

    @validates('quantity')
    def update_quantity(self, key, value):
        """When quantity is updated, updates the server.ram_total,
        server.ram_available, ram.available and server.ram_slot_available.
        """
        if value < 0:
            raise ValidationError('A quantidade precisa ser maior que zero.')
        elif self.quantity is None:
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

    def __str__(self):
        return self.hd.model + ' x ' + str(self.quantity)

    @validates('hd')
    def update_hd(self, key, value):
        if self.hd is None or self.hd == value:
            return value
        raise ValidationError("Não é possível alterar o modelo do HD. "
                              "Delete esse componente e crie outro.")

    @validates('quantity')
    def update_quantity(self, key, value):
        """ When quantity is updated, updates the server.hd_total,
        server.hd_available, server.ssd_total, server.ssd_available,
        hd.available and server.hd_slot_available.
        """
        if value < 0:
            raise ValidationError('A quantidade precisa ser maior que zero.')
        elif self.quantity is None:
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
        server_values['hd_slot_available'] = target.server.hd_slot_available - target.quantity
        connection.execute(Server.__table__.update()
                           .where(Server.__table__.c.id == target.server_id)
                           .values(**server_values))
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
        server_values['hd_slot_available'] = target.server.hd_slot_available - target.quantity
        connection.execute(Server.__table__.update()
                           .where(Server.__table__.c.id == target.server_id)
                           .values(**server_values))
        connection.execute(Hd.__table__.update()
                           .where(Hd.__table__.c.model == target.hd_model)
                           .values(available=target.hd.available + target.quantity))


class UserPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=False)
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'))
    start_date = db.Column(db.DateTime, default=func.now())
    end_date = db.Column(db.DateTime, default=func.now())

    plan = db.relationship('Plan', backref=db.backref('user_plan'))
    user = db.relationship('User', backref=db.backref('user_plan'))
    server = db.relationship('Server', backref=db.backref('user_plans'))

    @validates('server')
    def update_server(self, key, value):
        """When the user_plans updates, free all resources in the old server."""
        if self.server == value:
            return value
        plan = Plan.query.filter_by(id=self.plan_id).first()
        available_server = plan.available_servers(only_one=True, server_id=value.id)
        if available_server is None:
            raise ValidationError("Esse servidor não esta disponível.")
        server, used_gpus, total_ram, total_hd, total_ssd = available_server
        if self.server_id is not None:
            self.server.cores_available += plan.cpu.cores
            self.server.ram_available += total_ram
            self.server.hd_available += total_hd
            self.server.ssd_available += total_ssd
            free_gpus = {}
            for server_gpu in self.server.server_gpus:
                # percorre todas as GPUs do plano
                for plan_gpu in plan.plan_gpus:
                    # verifica se a GPU ja foi liberada antes, se não coloca o valor da utiliazaão dela pra zero
                    if server_gpu.gpu_model not in free_gpus:
                        free_gpus[server_gpu.gpu_model] = 0
                    # testa se a freq é a mesma e a capacidade é maior ou igual,
                    # levando em consideração se a gpu já foi liberada antes
                    if server_gpu.gpu.frequency == plan_gpu.gpu.frequency and \
                                            server_gpu.total_capacity - free_gpus[server_gpu.gpu_model] >= \
                                            plan_gpu.quantity * plan_gpu.gpu.ram:
                        # incrementa a utilização da gpu do servidor
                        server_gpu.available_capacity += plan_gpu.quantity * plan_gpu.gpu.ram
                        free_gpus[server_gpu.gpu_model] += plan_gpu.quantity * plan_gpu.gpu.ram
        return value


class UserPlanStats(db.Model):
    user_plan_id = db.Column(db.Integer, db.ForeignKey('user_plan.id'), nullable=False, primary_key=True)
    date = db.Column(db.DateTime, primary_key=True, default=func.now())
    cpu_usage = db.Column(db.Float)
    disk_usage = db.Column(db.Float)

    user_plan = db.relationship('UserPlan', backref=db.backref('user_plan_stats'))
