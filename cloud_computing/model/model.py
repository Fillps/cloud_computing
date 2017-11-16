# -*- coding: utf-8 -*-
from urllib import parse

import os
import psycopg2


def get_plan_by_title(plan_title, plans):
    """Searches for a plan in the list of plans by its title."""
    for plan in plans:
        if plan.title == plan_title:
            return plan
    return None


class Plan(object):
    def __init__(self, id, title, price, time, public, description):
        self.id = id
        self.title = title
        self.price = price
        self.time = time
        self.public = public
        self.description = description


class Database(object):
    conn = None
    cur = None
    publicPlans = None

    def __init__(self):
        self.connect()

    def connect(self):
        """ Connect to the PostgreSQL database server """
        if self.conn is None:
            try:
                parse.uses_netloc.append("postgres")
                url = parse.urlparse(os.environ["DATABASE_URL"])

                self.conn = psycopg2.connect(
                    database=url.path[1:],
                    user=url.username,
                    password=url.password,
                    host=url.hostname,
                    port=url.port)

                self.cur = self.conn.cursor()
            except(Exception, psycopg2.Error) as error:
                print(error)

    def disconnect(self):
        """ Disconnect from the PostgreSQL database server """
        if self.cur is not None:
            self.cur.close()
        if self.conn is not None:
            self.conn.close()

    def getPublicPlans(self):
        """ Return the public plans. If the plans are not updated, query from the database."""
        if self.publicPlans is None:
            try:
                self.cur.execute("SELECT id, titulo, preco, tempo, descricao "
                                 "FROM planos "
                                 "WHERE publico = TRUE;")
                rows = self.cur.fetchall()
                self.publicPlans = []
                for row in rows:
                    self.publicPlans.append(Plan(row[0], row[1], row[2], row[3], True, row[4]))

            except(Exception, psycopg2.DatabaseError) as error:
                print(error)
        return self.publicPlans

    def insertPlan(self, plan):
        """ Insert a plan in the table plans."""
        try:
            query = "INSERT INTO planos (titulo, preco, tempo, publico, descricao) " \
                    "VALUES (%S, %S, %S, %S, %S) " \
                    "RETURNING id;"
            values = [plan.title, plan.price, plan.time, plan.public, plan.description]
            self.cur.execute(query, values)
            plan.__setattr__('id', self.cur.fetchone()[0])
            self.conn.commit()
            if plan.public:
                self.publicPlans = None
            return plan
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)

