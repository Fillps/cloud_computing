# -*- coding: utf-8 -*-

from cloud_computing import app
from cloud_computing.model.models import Plan
from cloud_computing.controller.controller import Controller
from flask import render_template


@app.route('/')
def show_homescreen():
    """Shows the homescreen."""
    plans = Controller.get_plans()
    return render_template('shop-homepage.html', plans=plans)


@app.route('/<item_name>')
def show_item(item_name):
    """Shows the item detail page."""
    plan = Controller.get_plan_by_item_name(item_name)

    # TODO Implement test for error (plan == None)
    return render_template('shop-item.html', plan=plan)