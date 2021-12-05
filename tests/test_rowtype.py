"""Test rowtype argument for openers."""

from __future__ import unicode_literals

import csv

import pytest

from csv23.openers import open_reader, open_writer

PYTHONS = ['Graham Chapman', 'John Cleese', 'Terry Gilliam',
           'Eric Idle', 'Terry Jones', 'Michael Palin']

FIELDNAMES = ['first_name', 'last_name']

ROWDICTS = [dict(zip(FIELDNAMES, p.split())) for p in PYTHONS]


def test_rowtype_dict(filepath, fieldnames=FIELDNAMES, rowdicts=ROWDICTS):
    filename = str(filepath)

    with open_writer(filename, rowtype='dict', fieldnames=fieldnames) as w:
        assert isinstance(w, csv.DictWriter)
        w.writeheader()
        for r in rowdicts:
            w.writerow(r)

    with open_reader(filename, rowtype='dict') as r:
        assert isinstance(r, csv.DictReader)
        assert list(r) == rowdicts


@pytest.mark.parametrize('rowtype', ['nonrowtype', None, object(), []])
@pytest.mark.parametrize('func', [open_reader, open_writer])
def test_func_rowtype_invalid(mocker, func, rowtype):
    with pytest.raises(ValueError, match=r'invalid/unsupported rowtype'):
        func(mocker.sentinel.stream, rowtype=rowtype)


def test_open_writer_missing_fieldnames(mocker):
    with pytest.raises(TypeError, match='fieldnames'):
        open_writer(mocker.sentinel.stream, rowtype='dict')
