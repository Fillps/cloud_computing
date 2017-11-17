# -*- coding: utf-8 -*-

from flask_security import current_user, utils
from flask_admin import Admin
from flask_admin.contrib import sqla
from wtforms.fields import PasswordField

from cloud_computing import app
from cloud_computing.model.db_setup import db, User, Role, Plan


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
            model.password = utils.encrypt_password(model.password2)


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


# Initialize Flask-Admin
admin = Admin(
    app,
    'Management',
    base_template='admin.html',
    template_mode='bootstrap3',
)

# Add Flask-Admin views for Users and Roles
admin.add_view(UserAdmin(User, db.session))
admin.add_view(RoleAdmin(Role, db.session))
admin.add_view(PlanAdmin(Plan, db.session))
