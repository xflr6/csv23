# _common.py

from __future__ import unicode_literals

import io
import sys
import codecs
import locale
import contextlib

PY2 = sys.version_info.major == 2

ENCODING = 'utf-8'

DIALECT = 'excel'

ROWTYPE = 'list'

EIGHT_BIT_CLEAN = {
    'ascii',
    'cp437', 'cp720', 'cp737', 'cp775',
    'cp850', 'cp852', 'cp855', 'cp856', 'cp857', 'cp858',
    'cp860', 'cp861', 'cp862', 'cp863', 'cp864', 'cp865', 'cp866', 'cp869',
    'cp1006', 'cp1125',
    'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257', 'cp1258',
    'cp65001',
    'iso8859-1', 'iso8859-2', 'iso8859-3', 'iso8859-4', 'iso8859-5', 'iso8859-6',
    'iso8859-7', 'iso8859-8', 'iso8859-9', 'iso8859-10', 'iso8859-11', 'iso8859-13',
    'iso8859-14', 'iso8859-15', 'iso8859-16',
    'mac-cyrillic', 'mac-greek', 'mac-iceland', 'mac-latin2', 'mac-roman', 'mac-turkish',
    'utf-8',
}


def none_encoding():
    return locale.getpreferredencoding()


def is_8bit_clean(encoding):
    return codecs.lookup(encoding).name in EIGHT_BIT_CLEAN


@contextlib.contextmanager
def _open_csv(filename, open_kwargs, csv_func, dialect, reader_kwargs):
    """io.open() context manager returning csv_func(<file>, dialect=dialect)."""
    f = io.open(filename, **open_kwargs)
    try:
        yield csv_func(f, dialect=dialect, **reader_kwargs)
    finally:
        f.close()
