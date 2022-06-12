from __future__ import unicode_literals

import csv
import pytest
import warnings

from csv23.openers import open_reader
from csv23.readers import reader, UnicodeTextReader, UnicodeBytesReader

EXCEL = {}

QSLASH = {'quoting': csv.QUOTE_MINIMAL, 'escapechar': u'\\'}

SLASH = {'quoting': csv.QUOTE_NONE, 'escapechar': u'\\'}

ASCII = {'dialect': 'ascii'}

LINE_FORMAT_ROW = [
    ('spam,"eggs",spam spam,"eggs eggs"\r\n', EXCEL, ['spam', 'eggs', 'spam spam', 'eggs eggs']),
    ('"spam, spam","eggs\n eggs"\r\n', EXCEL, ['spam, spam', 'eggs\n eggs']),
    ('"""spam""","eggs ""eggs"" eggs"\r\n', EXCEL, ['"spam"', 'eggs "eggs" eggs']),
    ('sp\u00e4m,\u00ebggs\r\n', EXCEL, ['sp\u00e4m', '\u00ebggs']),
    ('sp\u00e5m,\u20acggs\r\n', EXCEL, ['sp\u00e5m', '\u20acggs']),
    ('spam,e\U0001d11e\U0001d11es\r\n', EXCEL, ['spam', 'e\U0001d11e\U0001d11es']),
    ('spam\r\n', SLASH, ['spam']),
    ('"spam\\\\eggs"\r\n', QSLASH, ['spam\\eggs']),
    ('spam\\\\eggs\r\n', QSLASH, ['spam\\eggs']),
    pytest.param('spam\x1fspam spam\x1feggs, eggs\x1e', ASCII,
                 ['spam', 'spam spam', 'eggs, eggs'],
                 marks=pytest.mark.xfail(reason='FIXME')),
]


@pytest.mark.parametrize('line, fmtparams, expected', LINE_FORMAT_ROW)
def test_open_reader(py2, filepath, encoding, line, fmtparams, expected, n=12):
    try:
        data = (line * n).encode(encoding)
    except UnicodeEncodeError:
        pytest.skip('impossible combination of line and encoding')

    filepath.write_bytes(data)

    if py2 and fmtparams == SLASH:
        with pytest.warns(UserWarning) as record:
            with open_reader(str(filepath), encoding=encoding, **fmtparams) as r:
                assert list(r) == [expected] * n
                assert len(record) == 1 and 'issue31590' in record[0].message.args[0]
    else:
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            with open_reader(str(filepath), encoding=encoding, **fmtparams) as r:
                assert list(r) == [expected] * n


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

    if py2 and fmtparams == SLASH:
        with pytest.warns(UserWarning) as record:
            r = reader([line] * n, encoding=encoding, **fmtparams)
        assert len(record) == 1 and 'issue31590' in record[0].message.args[0]
    else:
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            r = reader([line] * n, encoding=encoding, **fmtparams)
    assert isinstance(r, expected_type)
    assert hasattr(r, 'next' if py2 else '__next__')
    assert iter(r) is r
    assert r.line_num == 0
    assert next(r) == expected
    assert r.line_num == 1
    assert list(r) == [expected] * (n - 1)
    with pytest.raises(StopIteration):
        next(r)
