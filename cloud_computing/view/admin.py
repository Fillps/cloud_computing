# -*- coding: utf-8 -*-
import datetime
import pygal
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import validators
from flask_security import current_user, utils
from markupsafe import Markup
from sqlalchemy import func
from wtforms import ValidationError, SelectField
from wtforms.fields import PasswordField, IntegerField

from cloud_computing.model.models import ResourceRequests, PlanGpu, PlanRam, PlanHd, ServerGpu, ServerRam, ServerHd
from cloud_computing.utils.form_utils import ReadonlyCKTextAreaField, CKTextAreaField, ReadOnlyIntegerField

ADMIN_RESOURCES_REQUEST_MESSAGE_LENGTH = 100
REMOVE_ID = '2'
ADD_ID = '1'


class AdminView(sqla.ModelView):
    def is_accessible(self):
        """Prevent administration of Users unless the currently
        logged-in user has the "admin" role.
        """
        return current_user.has_role('admin')


class UserAdmin(AdminView):
    can_delete = False
    # Don't display the password on the list of Users
    column_list = ['id', 'name', 'last_name', 'email', 'cpf', 'cnpj',
                   'company', 'active', 'confirmed_at', 'roles']
    column_labels = dict(
        id='Id',
        name='Nome',
        last_name='Sobrenome',
        email='E-mail',
        cpf='CPF',
        cnpj='CNPJ',
        company='Empresa',
        active='Ativo',
        confirmed_at='Cadastrado em',
        roles='Papéis')

    # Don't include the standard password field when creating or editing a
    # User (but see below)
    form_columns = ['name', 'last_name', 'email', 'cpf', 'cnpj', 'company',
                    'active', 'confirmed_at', 'roles']

    # Automatically display human-readable names for the current and
    # available Roles when creating or editing a User
    column_auto_select_related = True

    column_searchable_list = ['id', 'name', 'last_name', 'email', 'cpf',
                              'cnpj', 'company', 'active', 'confirmed_at']

    def _comfirmed_at_formatter(view, context, model, name):
        if model.confirmed_at is not None:
            return model.confirmed_at.strftime('%d/%m/%Y')
        return model.confirmed_at

    column_formatters = {
        'confirmed_at': _comfirmed_at_formatter
    }

    def scaffold_form(self):
        """On the form for creating or editing a User, don't display a field
        corresponding to the model's password field. There are two reasons
        for this. First, we want to encrypt the password before storing in
        the database. Second, we want to use a password field (with the input
        masked) rather than a regular text field.
        """

        # Start with the standard form as provided by Flask-Admin. We've
        # already told Flask-Admin to exclude the password field from
        # this form
        form_class = super(UserAdmin, self).scaffold_form()

        # Add a password field, naming it "password2" and
        # labeling it "New Password"
        form_class.password2 = PasswordField('Nova Senha')

        return form_class

    def on_model_change(self, form, model, is_created):
        """This callback executes when the user saves changes to a newly-created
        or edited User -- before the changes are committed to the database"""
        # If the password field isn't blank...
        if len(model.password2):
            # ... then encrypt the new password prior to storing it in the
            # database. If the password field is blank, the existing password
            # in the database will be retained.
            model.password = utils.hash_password(model.password2)


class RoleAdmin(AdminView):
    column_searchable_list = ['name', 'description']
    column_labels = dict(name='Nome', description='Descrição')


class PlanAdmin(AdminView):
    column_list = ['title', 'auto_price', 'price', 'duration_months',
                   'cpu', 'os', 'plan_gpus', 'plan_rams', 'plan_hds', 'is_public']
    column_searchable_list = ['title', 'auto_price', 'duration_months', 'duration_months', 'shop_description',
                              'is_public']
    form_columns = ['title', 'auto_price', 'price', 'duration_months', 'cpu', 'gpu', 'ram',
                    'hd', 'os', 'shop_description', 'thumbnail',
                    'hero_image', 'is_public']

    form_columns = ['title', 'auto_price', 'price', 'duration_months', 'shop_description', 'thumbnail',
                    'hero_image', 'is_public', 'cpu', 'os', ]

    inline_models = [(PlanGpu,
                      dict(form_columns=['plan_id', 'gpu_model', 'gpu', 'quantity'],
                           column_labels=dict(quantity='Quantidade', gpu='GPU'))),
                     (PlanRam,
                      dict(form_columns=['plan_id', 'ram_model', 'ram', 'quantity'],
                           column_labels=dict(quantity='Quantidade', ram='RAM'))),
                     (PlanHd,
                      dict(form_columns=['plan_id', 'hd_model', 'hd', 'quantity'],
                           column_labels=dict(quantity='Quantidade', hd='HD')))]

    column_labels = dict(
        title='Título',
        price='Preço',
        duration_months='Duração em meses',
        shop_description='Descrição para a loja',
        cpu='CPU',
        plan_gpus='GPUs',
        plan_rams='RAMs',
        plan_hds='HDs',
        os='OS',
        is_public='É Público?',
        auto_price='Preço automático?')


class ResourceRequestsAdmin(AdminView):
    column_list = ['id', 'user_rel', 'message', 'message_date']
    form_columns = ['message', 'answer']
    column_searchable_list = ['id', 'message', 'message_date']
    column_labels = dict(id='Id', user_rel='Usuário', message='Mensagem',
                         message_date='Data da Mensagem', answer='Resposta')

    # Admins cannot delete or create requests, only answer them
    can_delete = False
    can_create = False

    # CKeditor - Text editor for the answer
    extra_js = ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']

    form_overrides = {
        # Message cannot be changed.
        'message': ReadonlyCKTextAreaField,
        'answer': CKTextAreaField
    }

    def _message_formatter(view, context, model, name):
        if len(model.message) > ADMIN_RESOURCES_REQUEST_MESSAGE_LENGTH:
            return Markup(model.message[:ADMIN_RESOURCES_REQUEST_MESSAGE_LENGTH]) + '...'
        else:
            return Markup(model.message)

    def _message_date_formatter(view, context, model, name):
        if model.message_date is not None:
            return model.message_date.strftime('%d/%m/%Y %H:%M:%S')
        return model.message_date

    column_formatters = {
        'message': _message_formatter,
        'message_date': _message_date_formatter
    }

    def get_count_query(self):
        """Count of the requests without answers."""
        return self.session.query(func.count(ResourceRequests.id)).filter(ResourceRequests.admin_id == None)

    def get_query(self):
        """Select only the requests without answers."""
        return super(ResourceRequestsAdmin, self).get_query().filter(ResourceRequests.admin_id == None)

    def on_model_change(self, form, model, is_created):
        """Check if the answer is empty. If is empty, raise an error.
        If is not empty save to the DB, updating the answer, admin_id and answer_date.
        """
        if len(model.answer):
            model.admin_id = current_user.id
            model.answer_date = func.now()
        else:
            raise validators.ValidationError('A resposta não pode estar vazia!')


class ComponentAdmin(AdminView):
    form_overrides = {
        'available': ReadOnlyIntegerField
    }

    def bigger_than_zero(form, field):
        if field.data <= 0:
            raise ValidationError("Esse campo precisa ser maior que zero.")

    form_args = dict(
        price=dict(validators=[bigger_than_zero]),
        quantity=dict(validators=[bigger_than_zero])
    )

    def scaffold_form(self):
        """Overrides the scaffold_form function. Adds the quantity field to the form."""
        form_class = super(ComponentAdmin, self).scaffold_form()

        form_class.addOrRemove = SelectField(
            "Selecione", choices=[(ADD_ID, 'Adicionar'),
                                  (REMOVE_ID, 'Remover')])

        form_class.quantity = IntegerField('Quantidade', default=0)

        return form_class

    def on_model_change(self, form, model, is_created):
        """Check if the available quantity and price are > 0."""
        if form.addOrRemove.data == REMOVE_ID:
            model.quantity = - model.quantity
        if is_created:
            if model.quantity >= 0:
                model.total = model.quantity
            else:
                raise ValidationError("Quantidade total precisa ser maior que zero.")
        else:
            if model.available + model.quantity >= 0:
                model.total = model.total + model.quantity
            else:
                raise ValidationError("Quantidade total precisa ser maior que zero.")


class CpuAdmin(ComponentAdmin):
    column_list = ['model', 'cores', 'frequency', 'price', 'total', 'available']
    form_columns = ['model', 'cores', 'frequency', 'price', 'available']
    column_searchable_list = column_list
    column_labels = dict(
        model='Modelo',
        cores='Nº de Núcleos',
        frequency='Frequência',
        price='Preço',
        total='Total',
        available='Disponíveis')
    form_args = dict(
        cores=dict(validators=[ComponentAdmin.bigger_than_zero]),
        frequency=dict(validators=[ComponentAdmin.bigger_than_zero]),
        price=dict(validators=[ComponentAdmin.bigger_than_zero]))


class GpuAdmin(ComponentAdmin):
    column_list = ['model', 'ram', 'frequency', 'price', 'total', 'available']
    form_columns = ['model', 'ram', 'frequency', 'price', 'available']
    column_searchable_list = column_list
    column_labels = dict(
        model='Modelo',
        ram='RAM',
        frequency='Frequência',
        price='Preço',
        total='Total',
        available='Disponíveis')
    form_args = dict(
        ram=dict(validators=[ComponentAdmin.bigger_than_zero]),
        frequency=dict(validators=[ComponentAdmin.bigger_than_zero]),
        price=dict(validators=[ComponentAdmin.bigger_than_zero]))


class RamAdmin(ComponentAdmin):
    column_list = ['model', 'capacity', 'price', 'total', 'available']
    form_columns = ['model', 'capacity', 'price', 'available']
    column_searchable_list = column_list
    column_labels = dict(
        model='Modelo',
        capacity='Capacidade',
        price='Preço',
        total='Total',
        available='Disponíveis')

    form_args = dict(
        capacity=dict(validators=[ComponentAdmin.bigger_than_zero]),
        price=dict(validators=[ComponentAdmin.bigger_than_zero])
    )


class HdAdmin(ComponentAdmin):
    column_list = ['model', 'capacity', 'is_ssd', 'price', 'total', 'available']
    form_columns = ['model', 'capacity', 'is_ssd', 'price', 'available']
    column_searchable_list = column_list
    column_labels = dict(
        model='Modelo',
        capacity='Capacidade',
        is_ssd='SSD',
        price='Preço',
        total='Total',
        available='Disponíveis')
    form_args = dict(
        capacity=dict(validators=[ComponentAdmin.bigger_than_zero]),
        price=dict(validators=[ComponentAdmin.bigger_than_zero]))


class ServerAdmin(AdminView):
    column_list = ['id', 'cpu', 'cores_available', 'gpu_slot_available', 'server_gpus', 'ram_slot_available', 'ram_available', 'hd_slot_available',
                   'hd_available', 'ssd_available', 'os']
    form_columns = ['cpu', 'gpu_slot_total', 'ram_slot_total', 'ram_max', 'hd_slot_total', 'os']

    inline_models = [(ServerGpu,
                      dict(form_columns=['server_id', 'gpu_model', 'gpu', 'quantity'],
                           column_labels=dict(quantity='Quantidade', gpu='GPU'))),
                     (ServerRam,
                      dict(form_columns=['server_id', 'ram_model', 'ram', 'quantity'],
                           column_labels=dict(quantity='Quantidade', ram='RAM'))),
                     (ServerHd,
                      dict(form_columns=['server_id', 'hd_model', 'hd', 'quantity'],
                           column_labels=dict(quantity='Quantidade', hd='HD')))]

    column_labels = dict(
        id='Id',
        cpu='CPU',
        cores_available='Núcleos',
        gpu_slot_available='GPU Slots',
        server_gpus='GPUs',
        ram_slot_available='RAM Slots',
        ram_available='RAM Disponível',
        hd_slot_available='HD Slots',
        hd_available='HD Disponível',
        ssd_available='SSD Disponível',
        os='OS',
        gpu_slot_total='Total de Slots de GPU',
        ram_slot_total='Total de Slots de RAM',
        hd_slot_total='Total de Slots de HD',
        ram_max='Capacidade Máxima de RAM (GB)'
    )
    def _cores_formatter(self, context, model, name):
        return '%s/%s' % (model.cores_available, model.cpu.cores)

    def _gpu_slot_formatter(self, context, model, name):
        return '%s/%s' % (model.gpu_slot_available,  model.gpu_slot_total)

    def _ram_slot_formatter(self, context, model, name):
        return '%s/%s' % (model.ram_slot_available,  model.ram_slot_total)

    def _hd_slot_formatter(self, context, model, name):
        return '%s/%s' % (model.hd_slot_available,  model.hd_slot_total)

    def _ram_formatter(view, context, model, name):
        return '%s/%s(%s) GB' % (str(model.ram_available), str(model.ram_total), str(model.ram_max))

    def _hd_formatter(view, context, model, name):
        return '%s/%s GB' % (str(model.hd_available), str(model.hd_total))

    def _ssd_formatter(view, context, model, name):
        return '%s/%s GB' % (str(model.ssd_available), str(model.ssd_total))

    column_formatters = dict(
        cores_available=_cores_formatter,
        gpu_slot_available=_gpu_slot_formatter,
        ram_slot_available=_ram_slot_formatter,
        hd_slot_available=_hd_slot_formatter,
        ram_available=_ram_formatter,
        hd_available=_hd_formatter,
        ssd_available=_ssd_formatter
    )

    def on_model_delete(self, model):
        if model.cpu.cores != model.cores_available:
            raise ValidationError("O servidor não pode ser excluido pois o CPU ainda está em uso.")
        if model.server_gpus:
            raise ValidationError("O servidor ainda possui GPUs. Remova elas antes.")
        if model.server_rams:
            raise ValidationError("O servidor ainda possui Memórias RAM. Remova elas antes.")
        if model.server_hds:
            raise ValidationError("O servidor ainda possui HDs. Remova eles antes.")


class UserPlanAdmin(AdminView):
    can_create = False
    can_edit = True
    can_view_details = True
    can_delete = False
    column_list = ['id', 'plan', 'server', 'start_date', 'end_date', 'time_remaining']
    column_details_list = ['id', 'plan', 'server', 'start_date', 'end_date', 'time_remaining', 'user_plan_stats']
    form_columns = ['server']

    column_labels = dict(
        id='Id',
        plan='Plano',
        server='Servidor',
        start_date='Data de Início',
        end_date='Data de Fim',
        time_remaining='Tempo Restante',
        user_plan_stats='Estatísticas de Uso')

    def _graph_formatter(view, context, model, name):
        date_l = []
        cpu_usage_l = []
        disk_usage_l = []
        for plan_stats in model.user_plan_stats:
            date_l.append(plan_stats.date)
            cpu_usage_l.append(plan_stats.cpu_usage)
            disk_usage_l.append(plan_stats.disk_usage)

        date_chart = pygal.Line(x_label_rotation=20)
        date_chart.x_labels = map(lambda d: d.strftime('%Y-%m-%d'), date_l)
        date_chart.add("Cpu_Usage", cpu_usage_l)
        date_chart.add("Disk_Usage", disk_usage_l)

        return Markup(date_chart.render(True))

    def _time_remaining(view, context, model, name):
        time_remaining = model.end_date - datetime.datetime.now()
        return str(time_remaining.days) + " dias restantes"

    def _start_date_formatter(view, context, model, name):
        if model.start_date is not None:
            return model.start_date.strftime('%d/%m/%Y')
        return model.start_date

    def _end_date_formatter(view, context, model, name):
        if model.end_date is not None:
            return model.end_date.strftime('%d/%m/%Y')
        return model.end_date

    column_formatters = {
        'user_plan_stats': _graph_formatter,
        'time_remaining': _time_remaining,
        'start_date': _start_date_formatter,
        'end_date': _end_date_formatter
    }
