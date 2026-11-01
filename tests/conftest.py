"""pytest configuration and shared fixtures."""

import locale

import pytest

ENCODING = ['utf-8', 'utf-16', 'utf-8-sig', 'latin9']

CLEAN = {'utf-8', 'latin9'}


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
