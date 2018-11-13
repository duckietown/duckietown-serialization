# coding=utf-8
from .library1 import *
from .ser1 import *
from .ser2 import *


def jobs_comptests(context):
    from comptests import jobs_registrar_simple
    jobs_registrar_simple(context)
