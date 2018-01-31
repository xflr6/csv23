# test_rowtype.py

from __future__ import unicode_literals

import csv

import pytest

from csv23.openers import open_reader, open_writer

PYTHONS = [
    'Graham Chapman', 'John Cleese', 'Terry Gilliam',
    'Eric Idle', 'Terry Jones', 'Michael Palin'
]

FIELDNAMES = ['first_name', 'last_name']

ROWDICTS = [dict(zip(FIELDNAMES, p.split())) for p in PYTHONS]


def test_rowtype_dict(filepath, fieldnames=FIELDNAMES, rowdicts=ROWDICTS):
    with open_writer(str(filepath), rowtype='dict', fieldnames=fieldnames) as writer:
        assert isinstance(writer, csv.DictWriter)
        writer.writeheader()
        for r in rowdicts:
            writer.writerow(r)

    with open_reader(str(filepath), rowtype='dict') as reader:
        assert isinstance(reader, csv.DictReader)
        assert list(reader) == rowdicts


@pytest.fixture
def stream(mocker):
    return mocker.sentinel.stream


@pytest.mark.parametrize('rowtype', ['nonrowtype', None, object(), []])
@pytest.mark.parametrize('func', [open_reader, open_writer])
def test_func_rowtype_invalid(stream, func, rowtype):
    with pytest.raises(ValueError, match=r'invalid/unsupported rowtype'):
        func(stream, rowtype=rowtype)


def test_open_writer_missing_fieldnames(stream):
    with pytest.raises(TypeError, match='fieldnames'):
        open_writer(stream, rowtype='dict')
