# coding=utf-8
from __future__ import unicode_literals

import yaml
from comptests import comptest, run_module_tests

from duckietown_serialization_ds1 import Serializable
from duckietown_serialization_ds1.context import Context, Library
from duckietown_serialization_ds1.serialization1 import from_json_dict2


class MyBase(Serializable):
    pass


class MyClass1(MyBase):

    __ds1_slots__ = ['x', 'y']

    def __init__(self, x, y):
        self.x = x
        self.y = y


# language=yaml
data1 = """\
one:
    ~MyClass1:
        x: 0
        y: 1
    
two:
    ~MyClass1:
        x: =MyClass1:one 
        y: =MyBase:one

"""

@comptest
def library1():

    c = Library()
    c.load_yaml_library_string(data1)
    one = c.load('MyClass1', 'two')
    print(one)
    two = c.load('MyClass1', 'two')
    print(two)
    print(c)


if __name__ == '__main__':
    run_module_tests()
