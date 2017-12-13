# -*- coding: utf-8 -*-

from cloud_computing.model.models import Plan


class Controller(object):
    """Initial implementation of the controller class."""
    @staticmethod
    def get_plans():
        """Queries the objects of type Plan on the database."""
        # TODO Determine the order of the list to show on front-end
        return Plan.query.filter_by(is_public=True)

    @staticmethod
    def get_plan_by_item_name(item_name):
        """Queries the database for the Plan of title 'item_name'."""
        return Plan.query.filter_by(title=item_name).first()
