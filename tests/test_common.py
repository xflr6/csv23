# test_common.py

from __future__ import unicode_literals

import pytest

from csv23._common import is_8bit_clean, csv_args


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
