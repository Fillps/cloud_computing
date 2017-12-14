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
    def get_plan_by_slug_url(slug_url):
        """Queries the database for the Plan of slug 'slug_url'."""
        return Plan.query.filter_by(slug_url=slug_url).first()
