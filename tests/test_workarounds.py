# test_workarounds.py

from __future__ import unicode_literals

import pytest

from csv23._workarounds import issue12178, issue31590


@pytest.mark.xfail(reason='https://bugs.python.org/issue12178')
def test_issue1278():
    assert not issue1278()


@pytest.mark.xfail(pytest.csv23.PY2, reason='https://bugs.python.org/issue31590')
def test_issue31590():
    assert not issue31590()
