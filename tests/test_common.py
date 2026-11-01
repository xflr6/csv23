import pytest

from csv23._common import is_8bit_clean


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
