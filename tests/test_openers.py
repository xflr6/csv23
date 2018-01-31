# test_openers.py

from __future__ import unicode_literals

import pytest

import itertools

from csv23.openers import _open_csv


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
