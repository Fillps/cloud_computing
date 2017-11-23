# -*- coding: utf-8 -*-
from flask import Blueprint, current_app, render_template
from cloud_computing.controller.controller import Controller

route_blueprint = Blueprint('home', __name__, url_prefix='')

@route_blueprint.route('/')
def show_homescreen():
    """Shows the homescreen."""
    plans = Controller.get_plans()
    return render_template(current_app.config['shop-homepage.html'], plans)


@route_blueprint.route('/<item_name>')
def show_item(item_name):
    """Shows the item detail page."""
    plan = Controller.get_plan_by_item_name(item_name)

    # TODO Implement test for error (plan == None)
    return render_template('shop-item.html', plan=plan)