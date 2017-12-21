from cloud_computing.view.admin import PlanAdmin, ServerAdmin
from flask_admin.contrib import sqla
from flask_security import current_user


class UnregisteredView(sqla.ModelView):
    def is_accessible(self):
        return True


class PlanUnregistered(PlanAdmin):
    column_list = ['title', 'price', 'duration_months',
                   'cpu', 'os', 'plan_gpus', 'plan_rams', 'plan_hds']
    column_searchable_list = ['title', 'duration_months', 'price']

    form_columns = ['duration_months', 'cpu', 'os']

    can_delete = False
    can_edit = False
    can_view_details = True

    def is_accessible(self):
        return current_user.is_authenticated is False or \
               current_user.has_role('end-user')


class ResourcesAvailable(ServerAdmin):
    column_list = ['id', 'cpu', 'cores_available', 'server_gpus',
                   'ram_available', 'hd_available', 'ssd_available', 'os']

    can_edit = False
    can_create = False
    can_view_details = True

    def is_accessible(self):
        return current_user.is_authenticated is False or \
               current_user.has_role('end-user')
