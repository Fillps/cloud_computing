# -*- coding: utf-8 -*-

from cloud_computing.model.models import Plan, Gpu, Ram, Hd, PlanGpu, PlanRam, PlanHd


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
        return Plan.query.filter(Plan.title.ilike("%" + search_input + "%")).filter_by(is_public=True)
