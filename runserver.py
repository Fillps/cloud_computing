#!/usr/bin/env python
# -*- coding: utf-8 -*-
from cloud_computing import create_app

if __name__ == '__main__':
    app = create_app('config.py')
    app.run()