# test_extras.py

from __future__ import unicode_literals

import collections

import pytest

from csv23.extras import NamedTupleReader, NamedTupleWriter


def test_NamedTupleReader():
    reader = NamedTupleReader(['spam,eggs\r\n', '1,2\r\n'])
    assert reader.dialect.delimiter == ','
    assert reader.line_num == 0
    assert reader.row_cls is None

    row = next(reader)
    assert row == ('1', '2')
    assert type(row) is reader.row_cls
    assert issubclass(reader.row_cls, tuple)
    assert reader.row_cls.__name__ == 'Row'
    assert reader.row_cls._fields == ('spam', 'eggs')
    assert not list(reader)


def test_NamedTupleReader_empty():
    reader = NamedTupleReader([])
    with pytest.raises(RuntimeError, match='missing header'):
        next(reader)


@pytest.mark.parametrize('header, match', [
    ('def,class\r\n', r'keyword'),
    ('spam.eggs,1-2\r\n', r'alphanumeric|identifiers'),
])
def test_NamedTupleReader_invalid_fieldname(header, match):
    reader = NamedTupleReader([header, '1,2\r\n'])
    with pytest.raises(ValueError, match=match):
        next(reader)


def test_NamedTupleReader_rename():
    reader = NamedTupleReader(['def,spam.eggs,spam\r\n', '1,2,3\r\n'], rename=True)
    row = next(reader)
    assert row == ('1', '2', '3')
    assert type(row) is reader.row_cls
    assert reader.row_cls._fields == ('_0', '_1', 'spam')


def test_NamedTupleReader_rename_func():
    rename = lambda x: x.replace('.', '_')
    reader = NamedTupleReader(['spam.eggs,spam\r\n', '1,2\r\n'], rename=rename)
    row = next(reader)
    assert row == ('1', '2')
    assert type(row) is reader.row_cls
    assert reader.row_cls._fields == ('spam_eggs', 'spam')


Row = collections.namedtuple('Row', ['column_1', 'column_2'])


@pytest.mark.parametrize('rows, lines', [
    ([Row('spam', 'spam spam'), Row('eggs', 'eggs, eggs')],
     ['column_1,column_2\r\n', 'spam,spam spam\r\n', 'eggs,"eggs, eggs"\r\n'])
])
def test_NamedTupleWriter(mocker, rows, lines):
    mock_open = mocker.mock_open()
    with mock_open('spam.csv', 'w') as f:
        writer = NamedTupleWriter(f)
        writer.writerows(rows)
    assert f.method_calls == [mocker.call.write(l) for l in lines]
