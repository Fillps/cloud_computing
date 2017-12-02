#!/usr/bin/env python
# -*- coding: utf-8 -*-
from cloud_computing import create_app

app = create_app('../configs/development.py')

if __name__ == '__main__':
    app.run()