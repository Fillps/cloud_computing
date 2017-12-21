# -*- coding: utf-8 -*-
from sqlalchemy import or_

from cloud_computing.model.models import Plan, Gpu, Ram, Hd, PlanGpu, PlanRam, PlanHd, Server


class Controller:
    """Initial implementation of the controller class."""

    @staticmethod
    def get_plans():
        """Queries the objects of type Plan on the database."""
        # TODO Determine the order of the list to show on front-end
        return Plan.query.filter_by(is_public=True)

    @staticmethod
    def get_plan_by_slug_url(slug_url):
        """Queries the database for the Plan of slug 'slug_url'."""
        return Plan.query.filter_by(slug_url=slug_url).first()

    @staticmethod
    def get_plan_gpu_list(plan_id):
        """Queries the database for the gpus related to the plan_id.

        Returns a list of pairs of Gpu objects with the quantity in
        their relationship table.
        """
        return Gpu.query.join(PlanGpu, Gpu.model == PlanGpu.gpu_model) \
            .add_columns(PlanGpu.quantity).filter(plan_id == PlanGpu.plan_id)

    @staticmethod
    def get_plan_ram_list(plan_id):
        """Queries the database for the ram memories related to the plan_id.

        Returns a list of pairs of Ram objects with the quantity in
        their relationship table.
        """
        return Ram.query.join(PlanRam, Ram.model == PlanRam.ram_model) \
            .add_columns(PlanRam.quantity).filter(plan_id == PlanRam.plan_id)

    @staticmethod
    def get_plan_hd_list(plan_id):
        """Queries the database for the hds related to the plan_id.

        Returns a list of pairs of Hd objects with the quantity in
        their relationship table.
        """
        return Hd.query.join(PlanHd, Hd.model == PlanHd.hd_model) \
            .add_columns(PlanHd.quantity).filter(plan_id == PlanHd.plan_id)

    @staticmethod
    def search_plan(search_input):
        """Searches for plans that match 'search_input' on the database."""
        return Plan.query.whooshee_search(search_input).filter_by(is_public=True)

    @staticmethod
    def get_available_resources():
        servers = Server.query.filter(Server.cores_available >= 0,
                                      Server.ram_available >= 0,
                                      or_(Server.hd_available >= 0,
                                          Server.ssd_available >= 0))
        data = []
        i = 1
        for server in servers:
            row = {}
            server_gpus = ""
            for gpu in server.server_gpus:
                server_gpus += gpu.__str__() + ' '
            row['row'] = i
            row['cpu'] = server.cpu_model
            row['cores_available'] = server.cores_available
            row['server_gpus'] = server_gpus
            row['ram_available'] = server.ram_available
            row['hd_available'] = server.hd_available
            row['ssd_available'] = server.ssd_available
            row['os'] = server.os_name
            data.append(row)
            i += 1

        # other column settings -> http://bootstrap-table.wenzhixin.net.cn/documentation/#column-options
        columns = [
            {
                "field": "row",  # which is the field's name of data key
                "title": "Opção",  # display as the table header's name
                "sortable": True,
            },
            {
                "field": "cpu",  # which is the field's name of data key
                "title": "CPU",  # display as the table header's name
                "sortable": True,
            },
            {
                "field": "cores_available",
                "title": "Núcleos disponíveis",
                "sortable": True,
            },
            {
                "field": "server_gpus",
                "title": "GPUs",
                "sortable": True,
            },
            {
                "field": "ram_available",
                "title": "RAM disponível",
                "sortable": True,
            },
            {
                "field": "hd_available",
                "title": "HD disponível",
                "sortable": True,
            },
            {
                "field": "ssd_available",
                "title": "SSD disponível",
                "sortable": True,
            },
            {
                "field": "os",
                "title": "OS",
                "sortable": True,
            }
        ]

        return data, columns
