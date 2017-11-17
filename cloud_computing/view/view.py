# -*- coding: utf-8 -*-

from cloud_computing import app
from cloud_computing.model.db_setup import Plan
from flask import render_template


@app.route('/')
def show_homescreen():
    """Shows the homescreen."""
    plans = Plan.query.all()
    return render_template('shop-homepage.html', plans=plans)


@app.route('/<item_name>')
def show_item(item_name):
    """Shows the item detail page."""
    plan = Plan.query.filter_by(title=item_name).first()

    # TODO Implement test for error (plan == None)
    return render_template('shop-item.html', plan=plan)