from __future__ import unicode_literals
from collections import defaultdict, namedtuple
import yaml
from contracts import contract, check_isinstance, indent
from contracts.interface import Where, format_where

from .serialization1 import looks_like_object, get_classes_for_object

__all__ = [
    'Context',
]


class LibraryDefinition(object):
    def __init__(self, spec, where):
        self.spec = spec
        self.depends = extract_depends(spec)
        self.where = where

    def __repr__(self):
        s = "LibraryDefinition"
        s += '\n\n' + indent(self.spec, '', 'spec:')
        s += '\n\n' + indent(self.depends, '', 'depends:')
        # s += '\n\n' + format_where(self.where)
        # s += '\n\n' + indent(self.where, '', 'where:')
        return s

    #
    # def __str__(self):
    #     return self.__repr__().encode('utf-8')


class Library(object):
    def __init__(self):
        self.type2entries = defaultdict(dict)
    #
    # def __str__(self):
    #     return self.__repr__().encode('utf-8')

    def __repr__(self):
        s = ""
        for k, v in self.type2entries.items():
            s += '\n%s' % k
            for name, info in v.items():
                s += '\n' + indent(info.__str__(), '', '%s: ' % name)
        return s

    def register_definition(self, klass_name, entry_name, v, where):
        d = self.type2entries[klass_name]
        if entry_name in d:
            msg = 'Already know %s' % entry_name
            raise ValueError(msg)  # XXX
        d[entry_name] = LibraryDefinition(v, where)

    @contract(s='string')
    def load_yaml_library_string(self, s, filename=None):
        y = yaml.load(s)
        check_isinstance(y, dict)
        for k, v in y.items():

            i = s.index(k)
            where = Where(string=s, character=i)
            where.filename = filename

            if looks_like_object(v):
                names = get_classes_for_object(v)
                for name in names:
                    self.register_definition(name, k, v, where)
            else:
                raise NotImplementedError()

    def load(self, collection_name, entry_name):
        d = self.type2entries[collection_name]
        if not entry_name in d:
            msg = 'Could not find %s' % entry_name
            raise ValueError(msg)
        return self.instance_spec(d)

    def instance_spec(self, d):
        pass


class Context(object):
    _default = None

    @classmethod
    def default(cls):
        if Context._default is None:
            Context._default = Context()
        return Context._default


def filter_recursive(x, f):
    if isinstance(x, list):
        return list(f([filter_recursive(_, f) for _ in x]))
    if isinstance(x, tuple):
        return tuple(f((filter_recursive(_, f) for _ in x)))
    elif isinstance(x, dict):
        return f(dict([(k, filter_recursive(v, f)) for k, v in x.items()]))
    else:
        return f(x)


def visitor(x, v):
    def f(_):
        v(_)
        return _

    return filter_recursive(x, f)


Reference = namedtuple('Reference', 'collection name')


def extract_depends(d):
    references = set()

    def f(x):
        try:
            reference = reference_from_ob(x)
            references.add(reference)
        except ValueError:
            pass
        return x

    visitor(d, f)
    return sorted(references)


import six


def reference_from_ob(x):
    """
        =Collection:name

    """
    if not isinstance(x, six.string_types):
        raise ValueError()
    if not x.startswith('='):
        raise ValueError()
    rest = x[1:]
    i = rest.index(':')
    collection = rest[:i]
    name = rest[i + 1:]
    return Reference(collection, name)
