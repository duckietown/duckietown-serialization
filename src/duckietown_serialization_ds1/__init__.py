# coding=utf-8
from __future__ import unicode_literals

__version__ = '2.0.0'

import logging

logger = logging.getLogger('dt-serialization')
logger.setLevel(logging.DEBUG)
logging.basicConfig()

from .exceptions import *
from .serialization1 import *
from .builtin_dt import *
from .cli1 import *
from .context import *
