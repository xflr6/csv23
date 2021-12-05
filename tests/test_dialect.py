"""Test dialect argument for readers and writers."""

from __future__ import unicode_literals

import csv

import pytest

from csv23.readers import UnicodeBytesReader
from csv23.writers import UnicodeBytesWriter

ATTRS = ('delimiter', 'lineterminator',
         'quoting', 'quotechar', 'doublequote',
         'escapechar',
         'skipinitialspace',
         'strict')

EXCEL = {'delimiter': u',',
         'quoting': csv.QUOTE_MINIMAL,
         'quotechar': u'"',
         'doublequote': True,
         'escapechar': None}

EXCEL_TAB = dict(EXCEL, delimiter=u'\t')

ARGS_FORMAT_DIALECT = [([], {}, csv.excel),
                       ([None], {}, csv.excel),
                       (['excel'], {}, csv.excel),
                       ([], EXCEL, csv.excel),
                       (['excel-tab'], {}, csv.excel_tab),
                       ([csv.excel_tab], {}, csv.excel_tab),
                       ([], EXCEL_TAB, csv.excel_tab)]


@pytest.mark.parametrize('args, fmtparams, expected', ARGS_FORMAT_DIALECT)
@pytest.mark.parametrize('cls', [UnicodeBytesReader, UnicodeBytesWriter])
def test_cls_dialect(mocker, cls, args, fmtparams, expected):
    stream = mocker.mock_open()()
    inst = cls(stream, *args, **fmtparams)
    assert dialect_attrs(inst.dialect) == dialect_attrs(expected)


def dialect_attrs(dialect, attrs=[a for a in ATTRS if a != 'strict']):
    result = {a: getattr(dialect, a) for a in attrs}
    result['strict'] = getattr(dialect, 'strict', False)
    return result
