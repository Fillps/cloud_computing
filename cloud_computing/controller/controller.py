# -*- coding: utf-8 -*-
from cloud_computing.model.model import Database, get_plan_by_title
from flask import render_template, session, flash, redirect, url_for, request
from cloud_computing import app

db = Database()

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    db.disconnect()

@app.route('/')
def show_homescreen():
    """Shows the homescreen."""
    return render_template('shop-homepage.html', plans=db.getPublicPlans())


@app.route('/<item_name>')
def show_item(item_name):
    """Shows the item detail page."""
    plan = get_plan_by_title(item_name, db.getPublicPlans())

    # TODO Implement test for error (plan == None)
    return render_template('shop-item.html', plan=plan)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs in the user."""
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_homescreen'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    """Logs out the user."""
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_homescreen'))

