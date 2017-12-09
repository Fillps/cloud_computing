# -*- coding: utf-8 -*-
from configs.common import *  # NOQA

# built-in constraints
DEBUG = True

SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:@localhost/cloud_computing'

try:
    from configs.local import *  # NOQA
except ImportError:
    pass