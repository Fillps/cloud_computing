# -*- coding: utf-8 -*-

from flask import flash, request
from flask_admin import expose
from flask_admin.babel import gettext
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import validators
from flask_admin.helpers import get_redirect_target
from flask_admin.model.helpers import get_mdict_item_or_list
from flask_security import current_user
from markupsafe import Markup
from sqlalchemy import func
from werkzeug.utils import redirect
from wtforms import BooleanField

from cloud_computing.model.models import ResourceRequests, CreditCard, Purchase, UserPlan, User
from cloud_computing.utils.form_utils import CKTextAreaField
from cloud_computing.view.admin import UserAdmin, UserPlanAdmin


USER_RESOURCES_REQUEST_MESSAGE_LENGTH = 50


class UserModelView(sqla.ModelView):
    def is_accessible(self):
        """Prevent administration of ResourceRequests unless the currently
        logged-in user has the "end-user" role.
        """
        return current_user.has_role('end-user')


class UserPlanView(UserPlanAdmin):
    can_edit = True
    form_excluded_columns = ['id', 'plan', 'server', 'start_date', 'end_date',
                             'user', 'purchases', 'user_servers', 'user_plan_stats']

    def scaffold_form(self):
        """Overrides the scaffold_form function. Adds the quantity field to the form."""
        form_class = super(UserPlanView, self).scaffold_form()

        form_class.renew = BooleanField('Deseja renovar o plano?')

        return form_class

    def on_model_change(self, form, model, is_created):
        if form.renew.data is True:
            self.session.add(Purchase(user=current_user,
                                      credit_card=current_user.credit_cards[0],
                                      plan=model.plan,
                                      user_plan=model))

    def get_count_query(self):
        """Count of the requests with the user_id equal to the current user."""
        return self.session.query(func.count(UserPlan.id)).filter(UserPlan.user_id == current_user.id)

    def get_query(self):
        """Select only the requests with the user_id equal to the current user."""
        return super(UserPlanView, self).get_query().filter(UserPlan.user_id == current_user.id)

    def is_accessible(self):
        """Prevent administration of ResourceRequests unless the currently
        logged-in user has the "end-user" role.
        """
        return current_user.has_role('end-user')


class PurchaseUser(UserModelView):
    can_view_details = True
    can_edit = False
    can_create = True
    can_delete = False

    column_list = ['id', 'plan', 'user_plan', 'credit_card', 'plan.price', 'date']
    column_labels = dict(
        id='Id',
        plan='Plano',
        credit_card='Cartão de Crédito',
        date='Data',
        user_plan='Contratação')
    form_columns = ['plan', 'credit_card']

    def get_count_query(self):
        """Count of the requests with the user_id equal to the current user."""
        return self.session.query(func.count(Purchase.id)).filter(Purchase.user_id == current_user.id)

    def get_query(self):
        """Select only the requests with the user_id equal to the current user."""
        return super(PurchaseUser, self).get_query().filter(Purchase.user_id == current_user.id)

    def on_model_change(self, form, model, is_created):
        model.user_id = current_user.id


class CreditCardUser(UserModelView):
    column_list = ['number', 'name', 'exp_date']
    form_columns = ['number', 'name', 'exp_date', 'cvv']
    column_labels = dict(number='Número', name='Nome', exp_date='Data de Vencimento', cvv='CVV')

    def _number_formatter(view, context, model, name):
        """Format the card number to show only the last 4 digits."""
        number_str = repr(model.number)
        return '****' + number_str[len(number_str) - 4:]

    def _exp_date_formatter(view, context, model, name):
        if model.exp_date is not None:
            return model.exp_date.strftime('%m/%Y')
        return model.exp_date

    column_formatters = {
        'number': _number_formatter,
        'exp_date': _exp_date_formatter
    }

    def get_count_query(self):
        """Count of the requests with the user_id equal to the current user."""
        return self.session.query(func.count(CreditCard.id)).filter(CreditCard.user_id == current_user.id)

    def get_query(self):
        """Select only the requests with the user_id equal to the current user."""
        return super(CreditCardUser, self).get_query().filter(CreditCard.user_id == current_user.id)

    def on_model_change(self, form, model, is_created):
        model.user_id = current_user.id

    def is_accessible(self):
        """Prevent administration of ResourceRequests unless the currently
        logged-in user has the "end-user" role.
        """
        return current_user.has_role('end-user')


class UserInfoUser(UserAdmin):
    can_create = False
    form_columns = ['name', 'last_name', 'email', 'cpf', 'cnpj', 'company']

    def get_count_query(self):
        """Count of the requests with the user_id equal to the current user."""
        return self.session.query(func.count(User.id)).filter(User.id == current_user.id)

    def get_query(self):
        """Select only the requests with the user_id equal to the current user."""
        return super(UserInfoUser, self).get_query().filter(User.id == current_user.id)

    def is_accessible(self):
        """Prevent administration of ResourceRequests unless the currently
        logged-in user has the "end-user" role.
        """
        return current_user.has_role('end-user')


class ResourceRequestsUser(UserModelView):
    # User can create, view and delete requests, but cannot edit them
    can_delete = True
    can_edit = False
    can_view_details = True

    column_list = ['id', 'message_date', 'message', 'admin_rel', 'answer_date', 'answer']
    column_searchable_list = ['id', 'message_date', 'message', 'answer_date', 'answer']
    column_details_list = ['id', 'message_date', 'message', 'admin_rel', 'answer_date', 'answer']
    form_excluded_columns = ['message_date', 'answer_date', 'answer', 'id', 'admin_rel', 'user_rel']
    column_labels = dict(
        id='Id',
        message_date='Data da Mensagem',
        admin_rel='Administrador',
        answer_date='Data da Resposta',
        answer='Resposta',
        message='Mensagem')

    # CKeditor - Text editor for the answer
    extra_js = ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']

    form_overrides = {
        'message': CKTextAreaField,
    }

    def _message_formatter(view, context, model, name):
        if model.message is not None and len(model.message) > USER_RESOURCES_REQUEST_MESSAGE_LENGTH:
            return Markup(model.message[:USER_RESOURCES_REQUEST_MESSAGE_LENGTH]) + '...'
        return Markup(model.message)

    def _answer_formatter(view, context, model, name):
        if model.answer is not None and len(model.answer) > USER_RESOURCES_REQUEST_MESSAGE_LENGTH:
            return Markup(model.answer[:USER_RESOURCES_REQUEST_MESSAGE_LENGTH]) + '...'
        return Markup(model.answer)

    def _message_formatter_details(view, context, model, name):
        return Markup(model.message)

    def _answer_formatter_details(view, context, model, name):
        return Markup(model.answer)

    def _message_date_formatter(view, context, model, name):
        if model.message_date is not None:
            return model.message_date.strftime('%d/%m/%Y %H:%M:%S')
        return model.message_date

    def _answer_date_formatter(view, context, model, name):
        if model.answer_date is not None:
            return model.answer_date.strftime('%d/%m/%Y %H:%M:%S')
        return model.answer_date

    column_formatters = {
        'message': _message_formatter,
        'answer': _answer_formatter,
        'message_date': _message_date_formatter,
        'answer_date': _answer_date_formatter
    }

    # Using the export format in the details_view.
    # This variable is going to be used in the function 'get_export_value', witch will be used in 'details_view'.
    column_formatters_export = {
        'message': _message_formatter_details,
        'answer': _answer_formatter_details,
        'message_date': _message_date_formatter,
        'answer_date': _answer_date_formatter
    }

    @expose('/details/')
    def details_view(self):
        """Override the details_view to use the export formatter."""
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_view_details:
            return redirect(return_url)

        request_id = get_mdict_item_or_list(request.args, 'id')

        if request_id is None:
            return redirect(return_url)

        request_model = self.get_one(request_id)

        if request_model is None:
            flash(gettext('O registro não existe.'), 'erro')
            return redirect(return_url)

        if self.details_modal and request.args.get('modal'):
            template = self.details_modal_template
        else:
            template = self.details_template

        return self.render(template,
                           model=request_model,
                           details_columns=self._details_columns,
                           get_value=self.get_export_value,
                           return_url=return_url)

    def get_count_query(self):
        """Number of requests made by the user."""
        return self.session.query(func.count(ResourceRequests.id)).filter(ResourceRequests.user_id == current_user.id)

    def get_query(self):
        """Select only the requests made by the user."""
        return super(ResourceRequestsUser, self).get_query().filter(ResourceRequests.user_id == current_user.id)

    def on_model_change(self, form, model, is_created):
        """Check if the message is empty, if it is raise an error,
        otherwise save to the db, creating a new resource request.
        """
        if len(model.message):
            model.user_id = current_user.id
            model.message_date = func.now()
        else:
            raise validators.ValidationError('A resposta não pode estar em branco!')
