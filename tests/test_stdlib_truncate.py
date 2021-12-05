"""Verify stdlib binary io behaviour of truncate(0).

- https://bugs.python.org/issue8840
- https://bugs.python.org/issue32228
- https://bugs.python.org/issue30250
- https://bugs.python.org/issue27261
- https://bugs.python.org/issue26158
"""

from __future__ import unicode_literals

import contextlib
import importlib

import pytest


@pytest.mark.parametrize(
    'module, cls',
    [pytest.param('cStringIO', 'StringIO', marks=pytest.csv23.py2only),
     ('io', 'BytesIO')])
def test_truncate_zero(module, cls):
    module = importlib.import_module(module)
    cls = getattr(module, cls)
    legacy = cls.__name__ == 'StringIO'

    if legacy:
        BytesIO = lambda: contextlib.closing(cls())  # noqa: E731, N806
    else:
        BytesIO = cls  # noqa: N806

    with BytesIO() as f:
        f.write(b'spam')
        assert f.tell() == 4

        f.truncate(0)
        assert f.tell() == 0 if legacy else 4

        f.write(b'eggs')
        assert f.tell() == 4 if legacy else 8
        assert f.getvalue() == b'eggs' if legacy else b'\x00\x00\00\x00eggs'
