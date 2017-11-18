#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from cloud_computing import app

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)