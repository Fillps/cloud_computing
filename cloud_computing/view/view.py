# -*- coding: utf-8 -*-

from flask import Blueprint, render_template
from cloud_computing.controller.controller import Controller


default_blueprint = Blueprint('default', __name__)


@default_blueprint.route('/')
def show_homescreen():
    """Shows the homescreen."""
    plans = Controller.get_plans()

    return render_template('shop-homepage.html', plans=plans)


@default_blueprint.route('/<slug_url>')
def show_item(slug_url):
    """Shows the item detail page."""
    plan = Controller.get_plan_by_slug_url(slug_url)
    gpu_list = Controller.get_plan_gpu_list(plan.id)
    ram_list = Controller.get_plan_ram_list(plan.id)
    hd_list = Controller.get_plan_hd_list(plan.id)

    return render_template('shop-item.html', plan=plan, gpu_list=gpu_list,
                           ram_list=ram_list, hd_list=hd_list)
