# -*- coding: utf-8 -*-

from configs.common import *  # NOQA

# TODO O que é NOQA? O que está acontecendo nesses arquivos?

DEBUG = True
TESTING = True

SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:@localhost/cloud_computing_tests'

try:
    from configs.local import *  # NOQA
except ImportError:
    pass
