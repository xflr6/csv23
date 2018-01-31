# test_common.py

from __future__ import unicode_literals

import pytest

import itertools

from csv23._common import is_8bit_clean, csv_args, _open_csv


@pytest.mark.parametrize('encoding, expected', [
    ('u8', True),
    ('u16', False),
    ('windows-1252', True),
    ('utf-16', False),
    ('IBM437', True),
    ('cp500', False),
    ('UTF-16BE', False),
    ('utf_8_sig', False),
])
def test_is_8bit_clean(encoding, expected):
    assert is_8bit_clean(encoding) == expected


@pytest.mark.parametrize('kwargs, expected_py2', [
    ({'delimiter': u','}, {'delimiter': b','}),
    ({'lineterminator': u'\r\n'}, {'lineterminator': b'\r\n'}),
    ({'quotechar': u'"'}, {'quotechar': b'"'}),
    ({'delimiter': u',', 'quotechar': None, 'doublequote': True},
     {'delimiter': b',', 'quotechar': None, 'doublequote': True}),
])
def test_csv_args(py2, kwargs, expected_py2):
    result = csv_args(kwargs)
    if py2:
        assert result == expected_py2
        assert all(not isinstance(v, unicode) for v in result.itervalues())
    else:
        assert result == kwargs
        assert all(not isinstance(v, bytes) for v in result.values())


@pytest.mark.parametrize('event', ['close', 'gc', RuntimeError])
def test_open_csv(mocker, mock_open, event):
    stream = mock_open.return_value
    csv_func = mocker.Mock(return_value=itertools.count())
    filename, dialect = mocker.sentinel.filename, mocker.sentinel.dialect

    def iterrows():
        with _open_csv(filename, {}, csv_func, dialect, {}) as reader:
            for row in reader:
                yield row

    r = iterrows()
    assert next(r) == 0
    mock_open.assert_called_once_with(filename)
    csv_func.assert_called_once_with(stream, dialect=dialect)
    stream.close.assert_not_called()

    assert next(r) == 1
    mock_open.assert_called_once()
    stream.close.assert_not_called()

    if event == 'close':
        r.close()
    elif event == 'gc':
        del r
    else:
        with pytest.raises(event):
            raise event
    mock_open.assert_called_once()
    stream.close.called_once_with()
