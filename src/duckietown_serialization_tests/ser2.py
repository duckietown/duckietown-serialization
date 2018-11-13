# coding=utf-8
from __future__ import unicode_literals

import json

import oyaml as yaml
from comptests import comptest, run_module_tests

from duckietown_serialization_ds1 import Serializable, Context


class MyPoint(Serializable):
    def __init__(self, x, y):
        self.x = x
        self.y = y


def test_dump_and_load(ob):
    context = Context()
    d = ob.as_json_dict(context=context)
    d_json = json.dumps(d, indent=4)
    print(d_json)
    d_yaml = yaml.safe_dump(d, default_flow_style=False)
    print(d_yaml)

    d2_json = json.loads(d_json)
    d2_yaml = yaml.load(d_yaml)

    ob2j = Serializable.from_json_dict(d2_json, context=context)
    ob2y = Serializable.from_json_dict(d2_yaml, context=context)

    w2 = ob2j.as_json_dict(context)
    ob2_json = json.dumps(w2, indent=4)


@comptest
def ser2a():
    ob = MyPoint(0, 0)
    test_dump_and_load(ob)


if __name__ == '__main__':
    run_module_tests()
