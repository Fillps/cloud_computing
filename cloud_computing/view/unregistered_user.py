from cloud_computing.view.admin import PlanAdmin, ServerAdmin
from flask_security import current_user


class ResourcesAvailable(ServerAdmin):
    column_list = ['id', 'cpu', 'cores_available', 'server_gpus',
                   'ram_available', 'hd_available', 'ssd_available', 'os']
    can_delete = False
    can_edit = False
    can_create = False
    can_view_details = True

    def is_accessible(self):
        return current_user.is_authenticated is False or \
               current_user.has_role('end-user')
