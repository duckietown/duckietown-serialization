# coding=utf-8
from __future__ import unicode_literals

import json
import traceback
from abc import ABCMeta
from collections import OrderedDict
from copy import deepcopy

import numpy as np
import six
from contracts import check_isinstance, contract
from future.utils import with_metaclass

from .exceptions import CouldNotDeserialize

__all__ = [
    'Serializable',
]


class Serializable0(object):
    __metaclass__ = ABCMeta

    GLYPH_CLASSES = '~'

    def as_json_dict(self, context):
        mro = type(self).mro()
        res = {}
        for k in mro:
            if k is object or k is Serializable0 or k is Serializable:
                continue
            # noinspection PyUnresolvedReferences
            if hasattr(k, 'params_to_json_dict'):
                try:
                    params = k.params_to_json_dict(self, context)
                except TypeError as e:
                    msg = 'Cannot call %s:params_to_json_dict(): %s' % (k.__name__, e)
                    raise TypeError(msg)
                if params is not None:
                    params = as_json_dict(params, context)
                    res[Serializable0.GLYPH_CLASSES + k.__name__] = params
        return res

    @classmethod
    def params_from_json_dict(cls, d, context):
        if d is None:
            return {}

        d2 = {}
        for k, v in d.items():
            d2[k] = d.pop(k)
        r = from_json_dict2(d2, context)

        check_isinstance(r, dict)
        return r

    @classmethod
    def params_from_json_dict_(cls, d, context):
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
            if hasattr(k, 'params_from_json_dict'):
                f0 = deepcopy(f)
                try:
                    f = k.params_from_json_dict(f0, context)
                except TypeError as e:
                    msg = 'Cannot invoke params_from_json_dict() on %s: %s' % (k.__name__, e)
                    raise TypeError(msg)

                if not isinstance(f, dict):
                    msg = 'Class %s returned not a dict with params_from_json_dict: %s ' % (k.__name__, f)
                    raise ValueError(msg)
                if f0:
                    msg = 'Error by %s:params_from_json_dict' % k.__name__
                    msg += '\nKeys not interpreted/popped: %s' % list(f0)
                    raise ValueError(msg)
            # print(cls, k, f)
            params.update(f)
        return params

    registered = OrderedDict()


def register_class(cls):
    Serializable0.registered[cls.__name__] = cls
    # logger.debug('Registering class %s' % cls.__name__)


class MetaSerializable(ABCMeta):
    def __new__(mcs, name, bases, class_dict):
        cls = ABCMeta.__new__(mcs, name, bases, class_dict)
        register_class(cls)
        return cls


class Serializable(with_metaclass(MetaSerializable, Serializable0)):

    @classmethod
    def from_json_dict(cls, d, context):
        return from_json_dict2(d, context)

    def params_to_json_dict(self, context):
        return vars(self)

    def __repr__(self):
        from duckietown_serialization_ds1 import Context
        context = Context()
        params = self.params_to_json_dict(context)
        if params:
            s = ",".join('%s=%s' % (k, v) for k, v in params.items())
            return '%s(%s)' % (type(self).__name__, s)
        else:
            return '%s()' % type(self).__name__


def as_json_dict(x, context):
    if six.PY2:
        if isinstance(x, unicode):
            return x
    if x is None:
        return None
    elif isinstance(x, (int, str, float)):
        return x
    elif isinstance(x, (list, tuple)):
        return [as_json_dict(_, context) for _ in x]
    elif isinstance(x, dict):
        return dict([(k, as_json_dict(v, context)) for k, v in x.items()])
    elif hasattr(x, 'as_json_dict'):  # Serializable fails in Python 3 for metaclass stuff
        return x.as_json_dict(context=context)
    elif isinstance(x, np.ndarray):
        return x.tolist()
    else:
        msg = 'Invalid class %s' % type(x).__name__
        msg += '\nmro: %s' % type(x).mro()
        msg += '\nCannot serialize {}'.format(x)
        raise ValueError(msg)


def from_json_dict2(d, context):
    if six.PY2:
        if isinstance(d, unicode):
            return d
    if d is None:
        return None
    elif isinstance(d, (int, str, float)):
        return d
    elif isinstance(d, list):
        return [from_json_dict2(_, context) for _ in d]
    elif isinstance(d, dict):
        if looks_like_object(d):
            return from_json_dict2_object(d, context)
        else:
            return dict([(k, from_json_dict2(v, context)) for k, v in d.items()])
    else:
        msg = 'Invalid class %s' % type(d).__name__
        msg += '\nCannot serialize {}'.format(d)
        raise ValueError(msg)


@contract(object_wire_presentation='dict')
def looks_like_object(object_wire_presentation):
    cd = {}
    for k in object_wire_presentation:
        it_is, name = is_encoded_classname(k)
        if it_is:
            cd[name] = object_wire_presentation[k]
    return len(cd) > 0


def get_classes_for_object(object_wire_presentation):
    """
        Returns all the classes declared and inferred from a wire presentation of an object.

    :param object_wire_presentation:
    :return:
    """
    res = set()
    for k in object_wire_presentation:
        it_is, name = is_encoded_classname(k)
        if name in Serializable.registered:
            klass = Serializable.registered[name]
            res.add(name)
            for base in klass.mro():
                if base.__name__ in Serializable.registered:
                    res.add(base.__name__)

        else:
            raise NotImplementedError()

    return res


add_fake = True


def create_fake_class(cname):
    class FakeClass(Serializable):
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    FakeClass.__name__ = str(cname)
    Serializable.registered[cname] = FakeClass


def from_json_dict2_object(d, context):
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
        res = klass.params_from_json_dict_(d2, context)
    except BaseException:
        msg = 'Cannot interpret data using %s' % klass.__name__
        msg += '\n\n%s' % json.dumps(d, indent=4)[:300]
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


def is_encoded_classname(x):
    if not isinstance(x, six.string_types):
        return False, None
    glyph = Serializable0.GLYPH_CLASSES

    if x.startswith(glyph):
        return True, x.replace(glyph, '')
    else:
        return False, None
