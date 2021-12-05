from __future__ import unicode_literals

import sys

import pytest

from csv23._workarounds import issue12178, issue31590


@pytest.mark.xfail(sys.version_info < (3, 10),
                   reason='https://bugs.python.org/issue12178')
def test_issue12178():
    assert not issue12178()


@pytest.mark.xfail(pytest.csv23.PY2,
                   reason='https://bugs.python.org/issue31590')
def test_issue31590():
    assert not issue31590()
