# -*- coding: utf-8 -*-

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash


# Create application
app = Flask(__name__)

# Debugging configuration
app.config.from_pyfile('config.cfg')

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'cloud_computing.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('CLOUD_COMPUTING_SETTINGS', silent=True)

# TODO Encapsulate these guys
class Plan(object):
    """Defines a plan object."""
    def __init__(self, title, price, description):
        self.title = title
        self.price = price
        self.description = description

class Data(object):
    """Defines a data object that queries the database on its constructor."""
    def __init__(self):
        db = get_db()
        cur = db.execute('select title, price, description from plans order by id asc')
        entries = cur.fetchall()

        self.plans = []

        for entry in entries:
            self.plans.append(Plan(entry[0], entry[1], entry[2]))


def get_plan_by_title(plan_title):
    """Searches for a plan in the list of plans by its title."""
    # TODO Shouldn't make a query every time, change this completely
    data = Data()

    for plan in data.plans:
        if plan.title == plan_title:
            return plan

    return None


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def db_test_data():
    """Creates test data in the database."""
    db = get_db()
    db.execute("insert into plans (title, price, description) values ('Plano básico', 19.99, 'Descrição do plano')")
    db.execute("insert into plans (title, price, description) values ('Plano intermediário', 29.99, 'Descrição do plano')")
    db.execute("insert into plans (title, price, description) values ('Plano avançado', 49.99, 'Descrição do plano')")
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    db_test_data()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_homescreen():
    """Shows the homescreen."""
    # TODO Again shouldn't make a query every time, change this
    data = Data()
    return render_template('shop-homepage.html', plans=data.plans)


@app.route('/<item_name>')
def show_item(item_name):
    """Shows the item detail page."""
    plan = get_plan_by_title(item_name)

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
