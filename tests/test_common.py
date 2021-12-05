from __future__ import unicode_literals

import pytest

from csv23._common import is_8bit_clean, csv_args


@pytest.mark.parametrize(
    'encoding, expected',
    [('u8', True),
     ('u16', False),
     ('windows-1252', True),
     ('utf-16', False),
     ('IBM437', True),
     ('cp500', False),
     ('UTF-16BE', False),
     ('utf_8_sig', False)])
def test_is_8bit_clean(encoding, expected):
    assert is_8bit_clean(encoding) == expected


@pytest.csv23.py2only
@pytest.mark.parametrize(
    'kwargs, expected',
    [({'delimiter': u','}, {'delimiter': b','}),
     ({'lineterminator': u'\r\n'}, {'lineterminator': b'\r\n'}),
     ({'quotechar': u'"'}, {'quotechar': b'"'}),
     ({'delimiter': u',', 'quotechar': None, 'doublequote': True},
      {'delimiter': b',', 'quotechar': None, 'doublequote': True})])
def test_csv_args_py2(kwargs, expected):
    result = csv_args(kwargs)
    assert result == expected
    assert all(not isinstance(v, unicode) for v in result.itervalues())


@pytest.csv23.py3only
def test_csv_args_py3():
    with pytest.raises(NotImplementedError):
        csv_args(None)
