# test_readers.py

from __future__ import unicode_literals

import csv

import pytest

from csv23.openers import open_reader
from csv23.readers import reader, UnicodeTextReader, UnicodeBytesReader

EXCEL = {}

SLASH = {'quoting': csv.QUOTE_NONE, 'escapechar': u'\\'}

LINE_FORMAT_ROW = [
    ('spam,"eggs",spam spam,"eggs eggs"\r\n', EXCEL, ['spam', 'eggs', 'spam spam', 'eggs eggs']),
    ('"spam, spam","eggs\n eggs"\r\n', EXCEL, ['spam, spam', 'eggs\n eggs']),
    ('"""spam""","eggs ""eggs"" eggs"\r\n', EXCEL, ['"spam"', 'eggs "eggs" eggs']),
    ('sp\u00e4m,\u00ebggs\r\n', EXCEL, ['sp\u00e4m', '\u00ebggs']),
    ('sp\u00e5m,\u20acggs\r\n', EXCEL, ['sp\u00e5m', '\u20acggs']),
    ('spam,e\U0001d11e\U0001d11es\r\n', EXCEL, ['spam', 'e\U0001d11e\U0001d11es']),
    ('spam\r\n', SLASH, ['spam']),
]


@pytest.mark.parametrize('line, fmtparams, expected', LINE_FORMAT_ROW)
def test_open_reader(py2, filepath, encoding, line, fmtparams, expected, n=12):
    try:
        data = (line * n).encode(encoding)
    except UnicodeEncodeError:
        pytest.skip('impossible combination of line and encoding')

    filepath.write_bytes(data)

    with pytest.warns(None) as record:
        with open_reader(str(filepath), encoding=encoding, **fmtparams) as r:
            assert list(r) == [expected] * n

    if py2 and fmtparams == SLASH:
        assert len(record) == 1 and 'issue31590' in record[0].message.args[0]
    else:
        assert not record


@pytest.mark.parametrize('line, fmtparams, expected', LINE_FORMAT_ROW)
def test_reader(py2, inner_encoding, line, fmtparams, expected, n=12):
    encoding = inner_encoding
    if encoding is False:
        expected_type = UnicodeTextReader if py2 else type(csv.reader([]))
    else:
        expected_type = UnicodeBytesReader
        try:
            line = line.encode(encoding)
        except UnicodeEncodeError:
            pytest.skip('impossible combination of line and encoding')
    with pytest.warns(None) as record:
        r = reader([line] * n, encoding=encoding, **fmtparams)
    if py2 and fmtparams == SLASH:
        assert len(record) == 1 and 'issue31590' in record[0].message.args[0]
    else:
        assert not record
    assert isinstance(r, expected_type)
    assert hasattr(r, 'next' if py2 else '__next__')
    assert iter(r) is r
    assert r.line_num == 0
    assert next(r) == expected
    assert r.line_num == 1
    assert list(r) == [expected] * (n - 1)
    with pytest.raises(StopIteration):
        next(r)
