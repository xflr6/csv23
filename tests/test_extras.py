# test_extras.py

from __future__ import unicode_literals

import pytest

from csv23.extras import NamedTupleReader


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
