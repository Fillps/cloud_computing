# -*- coding: utf-8 -*-

from configs.common import *  # NOQA

# TODO O que é NOQA? O que está acontecendo nesses arquivos?

DEBUG = True

try:
    from configs.local import *  # NOQA
except ImportError:
    pass
