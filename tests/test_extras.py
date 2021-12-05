from __future__ import unicode_literals

import collections

import pytest

from csv23.extras import NamedTupleReader, NamedTupleWriter


def test_NamedTupleReader():  # noqa: N802
    reader = NamedTupleReader(['spam,eggs\r\n', '1,2\r\n'])
    assert reader.dialect.delimiter == ','
    assert reader.line_num == 0
    assert reader.row_cls is None

    row = next(reader)
    assert row == ('1', '2')
    assert row == type(row)(spam='1', eggs='2')
    assert type(row) is reader.row_cls
    assert issubclass(reader.row_cls, tuple)
    assert reader.row_cls.__name__ == 'Row'
    assert reader.row_cls._fields == ('spam', 'eggs')
    for _ in range(2):
        assert reader.line_num == 2
        assert not list(reader)


def test_NamedTupleReader_empty():  # noqa: N802
    reader = NamedTupleReader([])
    with pytest.raises(RuntimeError, match='missing header'):
        next(reader)


@pytest.mark.parametrize(
    'header, match',
    [('1spam,eggs\r\n', r'start with a number|valid identifiers'),  # noqa: N802
     ('spam spam,eggs\r\n', r'alphanumeric|valid identifiers'),
     ('spam.spam,eggs\r\n', r'alphanumeric|valid identifiers'),
     ('spam-spam,eggs\r\n', r'alphanumeric|valid identifiers'),
     ('class,eggs,\r\n', r'keyword'),
     ('_spam,eggs\r\n', r'underscore')])
def test_NamedTupleReader_invalid_fieldname(header, match):
    reader = NamedTupleReader([header, '1,2\r\n'])
    with pytest.raises(ValueError, match=match):
        next(reader)


def test_NamedTupleReader_rename():  # noqa: N802
    lines = ['def,spam.eggs,spam\r\n', '1,2,3\r\n']
    reader = NamedTupleReader(lines, rename=True)
    row, = list(reader)

    assert row == ('1', '2', '3')
    assert row == type(row)(_0='1', _1='2', spam='3')
    assert type(row) is reader.row_cls
    assert reader.row_cls._fields == ('_0', '_1', 'spam')


def test_NamedTupleReader_rename_callable():  # noqa: N802
    lines = ['spam.eggs,spam\r\n', '1,2\r\n']
    reader = NamedTupleReader(lines, rename=lambda x: x.replace('.', '_'))
    row, = list(reader)

    assert row == ('1', '2')
    assert row == type(row)(spam_eggs='1', spam='2')
    assert type(row) is reader.row_cls
    assert reader.row_cls._fields == ('spam_eggs', 'spam')


def test_NamedTupleReader_row_name(row_name='Spam'):  # noqa: N802
    lines = ['spam,eggs\r\n', '1,2\r\n']
    reader = NamedTupleReader(lines, row_name=row_name)
    row, = list(reader)

    assert row == ('1', '2')
    assert row == type(row)(spam='1', eggs='2')
    assert type(row) is reader.row_cls
    assert reader.row_cls.__name__ == row_name


Row = collections.namedtuple('Row', ['column_1', 'column_2'])


@pytest.mark.parametrize(
    'rows, lines',
    [([Row('spam', 'spam spam'), Row('eggs', 'eggs, eggs')],  # noqa: N802
      ['column_1,column_2\r\n', 'spam,spam spam\r\n', 'eggs,"eggs, eggs"\r\n'])])
def test_NamedTupleWriter(mocker, rows, lines):
    mock_open = mocker.mock_open()
    with mock_open('spam.csv', 'w') as f:
        writer = NamedTupleWriter(f)
        assert writer.dialect.delimiter == ','
        writer.writerows(rows)
    assert f.method_calls == [mocker.call.write(l) for l in lines]
