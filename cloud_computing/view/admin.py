# -*- coding: utf-8 -*-
from flask import flash, request, current_app as app
from flask_admin import Admin, expose
from flask_admin.babel import gettext
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import validators
from flask_admin.form import rules
from flask_admin.helpers import get_redirect_target
from flask_admin.model.helpers import get_mdict_item_or_list
from flask_security import current_user, utils
from markupsafe import Markup
from sqlalchemy import func
from werkzeug.utils import redirect
from wtforms.fields import PasswordField


from cloud_computing.model.models import db, User, Role, Plan, ResourceRequests
from cloud_computing.utils.util import ReadonlyCKTextAreaField, CKTextAreaField

MAX_LEN_REQUEST_RESOURCES_ADMIN = 100
MAX_LEN_REQUEST_RESOURCES_USER = 50


class UserAdmin(sqla.ModelView):
    """Customized User model for SQL-Admin."""
    # Don't display the password on the list of Users
    column_exclude_list = ('password',)

    # Don't include the standard password field when creating or editing a
    # User (but see below)
    form_excluded_columns = ('password',)

    # Automatically display human-readable names for the current and
    # available Roles when creating or editing a User
    column_auto_select_related = True

    def is_accessible(self):
        """Prevent administration of Users unless the currently
        logged-in user has the "admin" role.
        """
        return current_user.has_role('admin')

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

    # This callback executes when the user saves changes to a newly-created
    # or edited User -- before the changes are committed to the database
    def on_model_change(self, form, model, is_created):
        # If the password field isn't blank...
        if len(model.password2):
            # ... then encrypt the new password prior to storing it in the
            # database. If the password field is blank, the existing password
            # in the database will be retained.
            model.password = utils.hash_password(model.password2)


class RoleAdmin(sqla.ModelView):
    """Customized Role model for SQL-Admin."""

    def is_accessible(self):
        """Prevent administration of Roles unless the currently
        logged-in user has the "admin" role.
        """
        return current_user.has_role('admin')


class PlanAdmin(sqla.ModelView):
    """Customized Plan model for SQL-Admin."""

    def is_accessible(self):
        """Prevent administration of Plans unless the currently
        logged-in user has the "admin" role.
        """
        return current_user.has_role('admin')


class ResourceRequestsAdmin(sqla.ModelView):
    """Customized ResourceRequests model for SQL-Admin."""
    column_list = ('id', 'user_id', 'message', 'message_date')
    form_columns = ('message', 'answer')

    # Admin cannot delete or create requests, only answer them.
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
        """Format the column with 100 characters."""
        if len(model.message)>MAX_LEN_REQUEST_RESOURCES_ADMIN:
            return Markup(model.message[:MAX_LEN_REQUEST_RESOURCES_ADMIN]) + '...'
        else:
            return Markup(model.message)

    def _message_date_formatter(view, context, model, name):
        if model.message_date is not None:
            return model.message_date.strftime('%d/%m/%Y %H:%M:%S')
        return model.message_date

    # format the column message with 100 characters.
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

    def is_accessible(self):
        """Prevent administration of ResourceRequests unless the currently
        logged-in user has the "admin" role.
        """
        return current_user.has_role('admin')


class ResourceRequestsUser(sqla.ModelView):
    """Customized ResourceRequests model for SQL-Admin."""

    # user cannot delete requests, only create and view them.
    can_delete = False
    can_edit = False
    can_view_details = True

    column_list = ('id', 'message_date', 'message', 'answer_date', 'answer')
    column_details_list = ('id', 'message_date', 'message', 'answer_date', 'answer')
    form_excluded_columns = ('message_date', 'answer_date', 'answer', 'id')

    # CKeditor - Text editor for the answer
    extra_js = ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']

    form_overrides = {
        'message': CKTextAreaField,
    }

    def _message_formatter(view, context, model, name):
        if model.message is not None and len(model.message) > MAX_LEN_REQUEST_RESOURCES_USER:
            return Markup(model.message[:MAX_LEN_REQUEST_RESOURCES_USER]) + '...'
        return Markup(model.message)

    def _answer_formatter(view, context, model, name):
        if model.answer is not None and len(model.answer) > MAX_LEN_REQUEST_RESOURCES_USER:
            return Markup(model.answer[:MAX_LEN_REQUEST_RESOURCES_USER]) + '...'
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

    # using the export format in the details_view
    column_formatters_export = {
        'message': _message_formatter_details,
        'answer': _answer_formatter_details,
        'message_date': _message_date_formatter,
        'answer_date': _answer_date_formatter
    }

    @expose('/details/')
    def details_view(self):
        """
            Override the details_view to use different formatter. The default formatter is the list_view formatter, but
            the export_view formatter is going to replace the formatter of details_view.

            Details model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_view_details:
            return redirect(return_url)

        id = get_mdict_item_or_list(request.args, 'id')
        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            flash(gettext('Record does not exist.'), 'error')
            return redirect(return_url)

        if self.details_modal and request.args.get('modal'):
            template = self.details_modal_template
        else:
            template = self.details_template

        return self.render(template,
                           model=model,
                           details_columns=self._details_columns,
                           get_value=self.get_export_value,
                           return_url=return_url)

    def get_count_query(self):
        """Count of the requests with the user_id equal to the current user."""
        return self.session.query(func.count(ResourceRequests.id)).filter(ResourceRequests.user_id == current_user.id)

    def get_query(self):
        """Select only the requests with the user_id equal to the current user."""
        return super(ResourceRequestsUser, self).get_query().filter(ResourceRequests.user_id == current_user.id)

    def on_model_change(self, form, model, is_created):
        """Check if the message is empty. If is empty, raise an error.
        If is not empty save to the DB, creating a new resource request.
        """
        if len(model.message):
            model.user_id = current_user.id
            model.message_date = func.now()
        else:
            raise validators.ValidationError('Answer cannot be empty!')

    def is_accessible(self):
        """Prevent administration of ResourceRequests unless the currently
        logged-in user has the "end-user" role.
        """
        return current_user.has_role('end-user')


