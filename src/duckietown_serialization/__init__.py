# coding=utf-8
__version__ = '1.0.2'

import logging
logger = logging.getLogger('dt-serialization')
logger.setLevel(logging.DEBUG)
logging.basicConfig()

from .exceptions import *
from .serialization1 import *
