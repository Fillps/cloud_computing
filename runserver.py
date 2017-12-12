#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cloud_computing import create_app
from cloud_computing.app_factory import AppFactory

# app = create_app('../configs/production.py')

factory = AppFactory()
app = factory.get_app()

if __name__ == '__main__':
    app.run()
