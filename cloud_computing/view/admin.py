# -*- coding: utf-8 -*-

from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import validators
from flask_security import current_user, utils
from markupsafe import Markup
from sqlalchemy import func
from wtforms import ValidationError, SelectField
from wtforms.fields import PasswordField, IntegerField

from cloud_computing.model.models import ResourceRequests
from cloud_computing.utils.util import ReadonlyCKTextAreaField, CKTextAreaField, ReadOnlyIntegerField

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
    # Don't display the password on the list of Users
    column_list = ['id', 'name', 'last_name', 'email', 'cpf', 'cnpj',
                   'company', 'active', 'confirmed_at', 'roles']

    # Don't include the standard password field when creating or editing a
    # User (but see below)
    form_columns = ['name', 'last_name', 'email', 'cpf', 'cnpj', 'company',
                    'active', 'confirmed_at', 'roles']

    # Automatically display human-readable names for the current and
    # available Roles when creating or editing a User
    column_auto_select_related = True

    column_searchable_list = ['id', 'name', 'last_name', 'email', 'cpf',
                              'cnpj', 'company', 'active', 'confirmed_at']

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
        form_class.password2 = PasswordField('New Password')

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


class PlanAdmin(AdminView):
    column_list = ['title', 'price', 'period', 'cpu', 'gpu', 'ram',
                   'hd', 'os', 'is_public']
    column_searchable_list = ['title', 'price', 'period', 'shop_description',
                              'is_public']
    form_columns = ['title', 'price', 'period', 'cpu', 'gpu', 'ram',
                    'hd', 'os', 'shop_description', 'thumbnail',
                    'hero_image', 'is_public']


class ResourceRequestsAdmin(AdminView):
    column_list = ['id', 'user_rel', 'message', 'message_date']
    form_columns = ['message', 'answer']
    column_searchable_list = ['id', 'message', 'message_date']

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
            raise validators.ValidationError('Answer cannot be empty!')


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

        form_class.addOrRemove = SelectField("Selecione", choices=[(ADD_ID, 'Adicionar'), (REMOVE_ID, 'Remover')])
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

    form_args = dict(
        cores=dict(validators=[ComponentAdmin.bigger_than_zero]),
        frequency=dict(validators=[ComponentAdmin.bigger_than_zero]),
        price=dict(validators=[ComponentAdmin.bigger_than_zero])
    )


class GpuAdmin(ComponentAdmin):
    column_list = ['model', 'ram', 'frequency', 'price', 'total', 'available']
    form_columns = ['model', 'ram', 'frequency', 'price', 'available']
    column_searchable_list = column_list

    form_args = dict(
        ram=dict(validators=[ComponentAdmin.bigger_than_zero]),
        frequency=dict(validators=[ComponentAdmin.bigger_than_zero]),
        price=dict(validators=[ComponentAdmin.bigger_than_zero])
    )


class RamAdmin(ComponentAdmin):
    column_list = ['model', 'capacity', 'price', 'total', 'available']
    form_columns = ['model', 'capacity', 'price', 'available']
    column_searchable_list = column_list

    form_args = dict(
        capacity=dict(validators=[ComponentAdmin.bigger_than_zero]),
        price=dict(validators=[ComponentAdmin.bigger_than_zero])
    )


class HdAdmin(ComponentAdmin):
    column_list = ['model', 'capacity', 'is_ssd', 'price', 'total', 'available']
    form_columns = ['model', 'capacity', 'is_ssd', 'price', 'available']
    column_searchable_list = column_list

    form_args = dict(
        capacity=dict(validators=[ComponentAdmin.bigger_than_zero]),
        price=dict(validators=[ComponentAdmin.bigger_than_zero])
    )


# TODO All the editing of a server should be in one screen
class ServerAdmin(AdminView):
    column_list = ['id', 'cpu', 'cores_available', 'gpu_slot_available', 'server_gpus', 'ram_slot_available', 'ram_max', 'ram_total',
                   'ram_available', 'hd_slot_available', 'hd_total', 'hd_available', 'ssd_total', 'ssd_available', 'os']
    form_columns = ['cpu', 'gpu_slot_total', 'ram_slot_total', 'ram_max', 'hd_slot_total', 'os']


class ServerComponentAdmin(AdminView):
    form_edit_rules = ['quantity', 'addOrRemove', 'add_quantity']
    form_overrides = {
        'quantity': ReadOnlyIntegerField
    }

    def bigger_than_zero(form, field):
        if field.data <= 0:
            raise ValidationError("Esse campo precisa ser maior que zero.")

    form_args = dict(
        add_quantity=dict(validators=[bigger_than_zero])
    )

    def scaffold_form(self):
        """Overrides the scaffold_form function. Adds the add_quantity field to the form."""
        form_class = super(ServerComponentAdmin, self).scaffold_form()

        form_class.addOrRemove = SelectField("Selecione", choices=[(ADD_ID, 'Adicionar'), (REMOVE_ID, 'Remover')])
        form_class.add_quantity = IntegerField('Quantidade')

        return form_class

    def on_model_change(self, form, model, is_created):
        """Adds the add_quantity field to the model quantity."""
        if form.addOrRemove.data == REMOVE_ID:
            model.add_quantity = - model.add_quantity
        model.quantity += model.add_quantity


class ServerGpuAdmin(ServerComponentAdmin):
    form_columns = ['server', 'gpu', 'quantity']


class ServerRamAdmin(ServerComponentAdmin):
    can_create = True


class ServerHdAdmin(ServerComponentAdmin):
    can_create = True