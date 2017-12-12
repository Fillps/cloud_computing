# -*- coding: utf-8 -*-

from flask import Blueprint, render_template
from cloud_computing.controller.controller import Controller


default_blueprint = Blueprint('default', __name__)


@default_blueprint.route('/')
def show_homescreen():
    """Shows the homescreen."""
    plans = Controller.get_plans()
    return render_template('shop-homepage.html', plans=plans)


@default_blueprint.route('/<item_name>')
def show_item(item_name):
    """Shows the item detail page."""
    plan = Controller.get_plan_by_item_name(item_name)
    return render_template('shop-item.html', plan=plan)
