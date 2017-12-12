#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cloud_computing.app_factory import AppFactory


factory = AppFactory('../configs/production.py')
app = factory.get_app()

if __name__ == '__main__':
    app.run()
