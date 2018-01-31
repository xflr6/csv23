# _dispatch.py

from __future__ import unicode_literals

import functools
import itertools

REGISTRY = {}

KIND = ('reader', 'writer')
ROWTYPE = ('list', 'dict')
LINETYPE = ('text', 'bytes')

KEYS = set(itertools.product(KIND, ROWTYPE, LINETYPE))


def register(kind, rowtype, linetype):
    key = kind, rowtype, linetype

    assert key in KEYS
    assert key not in REGISTRY

    def decorate(cls):
        REGISTRY[key] = cls
        return cls

    return decorate


register_reader, register_writer = (functools.partial(register, k) for k in KIND)


def get(kind, rowtype, linetype):
    key = kind, rowtype, linetype
    try:
        return REGISTRY[key]
    except (KeyError, TypeError):
        assert kind in KIND and linetype in LINETYPE
        raise ValueError('invalid/unsupported rowtype: %r' % rowtype)


get_reader, get_writer = (functools.partial(get, k) for k in KIND)
