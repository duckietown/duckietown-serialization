# coding=utf-8
import json
import traceback
from abc import ABCMeta
from collections import OrderedDict
from copy import deepcopy

import numpy as np

from .exceptions import CouldNotDeserialize

__all__ = ['Serializable']

GLYPH = '~'


class Serializable0(object):
    __metaclass__ = ABCMeta

    def __repr__(self):
        params = self.params_to_json_dict()
        if params:
            s = ",".join('%s=%s' % (k, v) for k, v in params.items())
            return '%s(%s)' % (type(self).__name__, s)
        else:
            return '%s()' % type(self).__name__

    def as_json_dict(self):
        mro = type(self).mro()
        res = {}
        for k in mro:
            if k is object or k is Serializable0 or k is Serializable:
                continue
            # noinspection PyUnresolvedReferences
            if hasattr(k, 'params_to_json_dict'):
                params = k.params_to_json_dict(self)
                if params is not None:
                    params = as_json_dict(params)

                    res[GLYPH + k.__name__] = params
        return res

    @classmethod
    def params_from_json_dict(cls, d):
        return from_json_dict2(d)

    @classmethod
    def params_from_json_dict_(cls, d):
        if not isinstance(d, dict):
            msg = 'Expected d to be a dict, got %s' % type(d).__name__
            raise ValueError(msg)
        params = {}
        mro = cls.mro()
        for k in mro:
            if k is object or k is Serializable0 or k is Serializable:
                continue
            kk = k.__name__
            if kk not in d:
                f = {}
            else:
                f = d[kk]
            f = k.params_from_json_dict(f)
            # print(cls, k, f)
            params.update(f)
        return params

    registered = OrderedDict()


from future.utils import with_metaclass


def register_class(cls):
    Serializable0.registered[cls.__name__] = cls
    print('registering %s' % cls.__name__)


class MetaSerializable(ABCMeta):
    def __new__(mcs, name, bases, class_dict):
        cls = type.__new__(mcs, name, bases, class_dict)
        register_class(cls)
        return cls


class Serializable(with_metaclass(MetaSerializable, Serializable0)):

    @classmethod
    def from_json_dict(cls, d):
        return from_json_dict2(d)

    def params_to_json_dict(self):
        return vars(self)


import six


def as_json_dict(x):
    if six.PY2:
        if isinstance(x, unicode):
            return x
    if x is None:
        return None
    elif isinstance(x, (int, str, float)):
        return x
    elif isinstance(x, list):
        return [as_json_dict(_) for _ in x]
    elif isinstance(x, dict):
        return dict([(k, as_json_dict(v)) for k, v in x.items()])
    elif isinstance(x, Serializable0):  # Serializable fails in Python 3 for metaclass stuff
        return x.as_json_dict()
    elif isinstance(x, np.ndarray):
        return x.tolist()
    else:
        msg = 'Invalid class %s' % type(x).__name__
        msg += '\nCannot serialize {}'.format(x)
        raise ValueError(msg)


def from_json_dict2(d):
    if d is None:
        return None
    elif isinstance(d, (int, str, float)):
        return d
    elif isinstance(d, list):
        return [from_json_dict2(_) for _ in d]
    elif isinstance(d, dict):
        if looks_like_object(d):
            return from_json_dict2_object(d)
        else:
            return dict([(k, from_json_dict2(v)) for k, v in d.items()])


def looks_like_object(d):
    cd = {}
    for k in d:
        it_is, name = is_encoded_classname(k)
        if it_is:
            cd[name] = d[k]
    return len(cd) > 0


add_fake = True


def create_fake_class(cname):
    class FakeClass(Serializable):
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    FakeClass.__name__ = str(cname)
    Serializable.registered[cname] = FakeClass


def from_json_dict2_object(d):
    if not isinstance(d, dict):
        msg = 'Expected dict for %s' % d
        raise CouldNotDeserialize(msg)

    # find out how many classes declarations there are
    cd = {}
    for k in d:
        it_is, name = is_encoded_classname(k)
        if it_is:
            cd[name] = d[k]

    # find out whether they are registered
    for cname in cd:
        if cname not in Serializable.registered:
            if add_fake:
                create_fake_class(cname)
            else:
                msg = 'Class %s not registered' % cname
                raise CouldNotDeserialize(msg)

    ordered = sorted(cd, key=lambda x: list(Serializable.registered).index(x), reverse=True)

    cname0 = ordered[0]
    klass = Serializable.registered[cname0]

    d2 = deepcopy(cd)
    try:
        res = klass.params_from_json_dict_(d2)
    except BaseException:
        msg = 'Cannot interpret data using %s' % klass.__name__
        msg += '\n\n%s' % json.dumps(d, indent=4)[:100]
        msg += '\n\n%s' % traceback.format_exc()
        raise CouldNotDeserialize(msg)

    try:
        out = klass(**res)
    except BaseException:
        msg = 'Cannot deserialize.'
        msg += '\ncd: %s' % cd
        msg += '\nklass: %s' % klass
        msg += '\nparams: %s' % res
        msg += '\n\n' + traceback.format_exc()
        raise CouldNotDeserialize(msg)

    return out
    #
    # msg = 'Cannot interpret any of %s' % list(d)
    # raise CouldNotDeserialize(msg)


def is_encoded_classname(x):
    if x.startswith(GLYPH):
        return True, x.replace(GLYPH, '')
    else:
        return False, None
