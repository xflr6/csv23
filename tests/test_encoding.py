"""Test endoding argument for openers, readers, and writers."""

from __future__ import unicode_literals

import pytest

import csv23._dispatch
from csv23.openers import open_reader, open_writer
from csv23.readers import reader
from csv23.writers import writer


@pytest.fixture
def stream(mocker):
    return mocker.sentinel.stream


@pytest.mark.parametrize(
    'func, cls_key, mode',
    [(open_reader, ('reader', 'list', 'text'), 'r'),
     (open_writer, ('writer', 'list', 'text'), 'w')])
def test_open_func_encoding_none(mocker, mock_open, stream,
                                 func, cls_key, mode, nonclean_none_encoding):
    mock_cls = mocker.create_autospec(csv23._dispatch.REGISTRY[cls_key])
    mocker.patch.dict('csv23._dispatch.REGISTRY', {cls_key: mock_cls})
    with func(stream, encoding=None) as f:
        assert f is mock_cls.return_value
        mock_cls.assert_called_once_with(mock_open.return_value, dialect='excel')
    mock_open.assert_called_once_with(stream, encoding=nonclean_none_encoding,
                                      mode=mode, newline='')


@pytest.mark.parametrize(
    'func, cls_path',
    [(reader, 'csv23.readers.UnicodeBytesReader'),
     (writer, 'csv23.writers.UnicodeBytesWriter')])
def test_func_encoding_none(mocker, stream, func, cls_path, none_encoding):
    mock_cls = mocker.patch(cls_path, autospec=True)
    assert func(stream, encoding=None) is mock_cls.return_value
    mock_cls.assert_called_once_with(stream, 'excel', none_encoding)


@pytest.mark.parametrize('func', [reader, writer])
def test_reader_encoding_nonclean(stream, func, nonclean_encoding):
    with pytest.raises(NotImplementedError):
        func(stream, encoding=nonclean_encoding)
