# test_writers.py

from __future__ import unicode_literals

import io
import csv

import pytest

from csv23.openers import open_writer
from csv23.writers import writer, UnicodeTextWriter, UnicodeBytesWriter
from csv23._common import is_8bit_clean

if not pytest.csv23.PY2:
    from csv23.writers import _UnicodeTextWriter

EXCEL = {}

QSLASH = {'quoting': csv.QUOTE_MINIMAL, 'escapechar': u'\\'}

SLASH = {'quoting': csv.QUOTE_NONE, 'escapechar': u'\\'}

ROW_FORMAT_LINE = [
    (['spam', 'spam spam', 'eggs, eggs'], EXCEL, 'spam,spam spam,"eggs, eggs"\r\n'),
    (['spam\n eggs', '"spam"', 'eggs "eggs" eggs'], EXCEL, '"spam\n eggs","""spam""","eggs ""eggs"" eggs"\r\n'),
    (['sp\u00e4m', '\u00ebggs'], EXCEL, 'sp\u00e4m,\u00ebggs\r\n'),
    (['sp\u00e5m', '\u20acggs'], EXCEL, 'sp\u00e5m,\u20acggs\r\n'),
    (['spam', 'e\U0001d11e\U0001d11es'], EXCEL, 'spam,e\U0001d11e\U0001d11es\r\n'),
    (['spam\\eggs'], QSLASH, '"spam\\\\eggs"\r\n'),
    (['spam\\eggs'], SLASH, 'spam\\\\eggs\r\n'),
]


@pytest.mark.parametrize('row, fmtparams, expected', ROW_FORMAT_LINE)
def test_open_writer(py2, filepath, encoding, row, fmtparams, expected, n=12):
    try:
        expected.encode(encoding)
    except UnicodeEncodeError:
        pytest.skip('impossible combination of row and encoding')

    write_n = len(expected.encode(encoding) if py2 and is_8bit_clean(encoding) else expected)

    filename = str(filepath)

    with open_writer(filename, encoding=encoding, **fmtparams) as w:
        written = w.writerow(row)
        w.writerows([row] * (n - 1))

    with io.open(filename, encoding=encoding, newline='') as f:
        line = f.read()

    assert line == expected * n
    assert written == write_n


@pytest.mark.parametrize('row, fmtparams, expected', ROW_FORMAT_LINE)
def test_writer(mocker, py2, filepath, inner_encoding,
                row, fmtparams, expected, n=12):
    encoding = inner_encoding
    if encoding is False:
        if py2:
            expected_type = UnicodeTextWriter
        elif (fmtparams.get('escapechar')
              and fmtparams.get('quoting', csv.QUOTE_MINIMAL) != csv.QUOTE_NONE):
            expected_type = _UnicodeTextWriter
        else:
            expected_type = type(csv.writer(mocker.mock_open()()))
        write_n = len(expected)
        file_encoding = 'utf-8'
        open_kwargs = {'mode': 'w', 'encoding': file_encoding, 'newline': ''}
    else:
        expected_type = UnicodeBytesWriter
        try:
            write_n = len(expected.encode(encoding))
        except UnicodeEncodeError:
            pytest.skip('impossible combination of row and encoding')
        file_encoding = encoding
        open_kwargs = {'mode': 'wb'}

    filename = str(filepath)

    with io.open(filename, **open_kwargs) as f:
        w = writer(f, encoding=encoding, **fmtparams)
        assert isinstance(w, expected_type)
        written = w.writerow(row)
        w.writerows([row] * (n - 1))

    with io.open(filename, encoding=file_encoding, newline='') as f:
        line = f.read()

    assert line == expected * n
    assert written == write_n
