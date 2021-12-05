"""pytest configuration and shared fixtures."""

from __future__ import unicode_literals

import argparse
import locale
import sys

import pytest

PY2 = (sys.version_info.major == 2)

ENCODING = ['utf-8', 'utf-16', 'utf-8-sig', 'latin9']

CLEAN = {'utf-8', 'latin9'}


def pytest_configure(config):
    py2only = pytest.mark.skipif(not PY2, reason='Python 2 only')
    py3only = pytest.mark.skipif(PY2, reason='Python 3 only')
    pytest.csv23 = argparse.Namespace(PY2=PY2, py2only=py2only, py3only=py3only)


@pytest.fixture(scope='session')
def py2():
    return PY2


@pytest.fixture(params=ENCODING)
def encoding(request):
    return request.param


@pytest.fixture(params=[False] + [e for e in ENCODING if e in CLEAN])
def inner_encoding(request):
    return request.param


@pytest.fixture(scope='session')
def none_encoding():
    return locale.getpreferredencoding()


@pytest.fixture(scope='session')
def nonclean_encoding():
    return next(e for e in ENCODING if e not in CLEAN)


@pytest.fixture
def nonclean_none_encoding(mocker, nonclean_encoding):
    mocker.patch('locale.getpreferredencoding', autospec=True,
                 return_value=nonclean_encoding)
    yield nonclean_encoding


@pytest.fixture
def mock_open(mocker):
    yield mocker.patch('io.open', mocker.mock_open())


@pytest.fixture
def filepath(tmp_path):
    return tmp_path / 'spam.csv'
