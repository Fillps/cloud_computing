# -*- coding: utf-8 -*-

from cloud_computing.model import models


def test_user_model(user_data):
    users = models.User.query.all()
    assert len(users) == len(user_data)


def test_plan_model(plan_data):
    plans = models.Plan.query.all()
    assert len(plans) == len(plan_data)
