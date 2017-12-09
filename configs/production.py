# -*- coding: utf-8 -*-
from configs.common import *  # NOQA

DEBUG = True

try:
    from configs.local import *  # NOQA
except ImportError:
    pass