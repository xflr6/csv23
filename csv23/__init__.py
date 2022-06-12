# csv23 - python 2 uniocde csv compat adapted from stdlib recipe

"""Python 2/3 unicode CSV compatibility layer and convenience functions."""

# TODO: add csv.Sniffer

from __future__ import unicode_literals

from csv import (QUOTE_MINIMAL, QUOTE_ALL, QUOTE_NONNUMERIC, QUOTE_NONE,
                 Error, Dialect, excel, excel_tab, field_size_limit,
                 register_dialect, get_dialect, list_dialects,
                 unregister_dialect)

from ._common import ENCODING, DIALECT, ROWTYPE
from .dialects import unix_dialect
from .extras import NamedTupleReader, NamedTupleWriter
from .openers import open_reader, open_writer
from .readers import reader, DictReader
from .writers import writer, DictWriter

from .shortcuts import read_csv, write_csv

__all__ = ['open_csv',
           'open_reader', 'open_writer',
           'iterrows',
           'reader', 'writer',
           'DictReader', 'DictWriter',
           'unix_dialect',
           'NamedTupleReader', 'NamedTupleWriter',
           'read_csv', 'write_csv']

__all__ += ['QUOTE_MINIMAL', 'QUOTE_ALL', 'QUOTE_NONNUMERIC', 'QUOTE_NONE',
            'Error', 'Dialect', 'excel', 'excel_tab', 'field_size_limit',
            'register_dialect', 'get_dialect', 'list_dialects',
            'unregister_dialect']

__title__ = 'csv23'
__version__ = '0.3.4'
__author__ = 'Sebastian Bank <sebastian.bank@uni-leipzig.de>'
__license__ = 'MIT, see LICENSE.txt'
__copyright__ = 'Copyright (c) 2018-2022 Sebastian Bank'

_OPEN_FUNCS = {'r': open_reader, 'w': open_writer}


def open_csv(filename, mode='r', encoding=ENCODING, dialect=DIALECT,
             rowtype=ROWTYPE, **fmtparams):
    r"""Context manager returning a CSV reader/writer (closing the file on exit).

    Args:
        filename: File (name) argument for the :func:`py:io.open` call.
        mode (str): ``'r'`` for a :func:`csv23.reader`, ``'w'`` for a :func:`csv23.writer`.
        encoding (str): Name of the encoding used to de/encode the file content.
        dialect: CSV dialect argument for the :func:`csv23.reader`/:func:`csv23.writer`.
        rowtype (str):
            ``'list'`` for a :func:`csv23.reader`/:func:`csv23.writer`,
            ``'dict'`` for a :class:`csv23.DictReader`/:class:`csv23.DictWriter`,
            ``'namedtuple'`` for a :class:`csv23.NamedTupleReader`/:class:`csv23.NamedTupleWriter`.
        \**fmtparams: Keyword arguments (formatting parameters) for the
            :func:`csv23.reader`/:func:`csv23.writer` (must include
            ``fieldnames`` if ``mode='w'`` and ``rowtype='dict'``).

    Returns:
        A context manager returning a Python 3 :func:`py3:csv.reader`/:func:`py3:csv.writer` stand-in when entering.

    >>> row = [u'Wonderful Spam', u'Lovely Spam']
    >>> with open_csv('spam.csv', 'w') as writer:  # doctest: +SKIP
    ...     writer.writerow(row)
    >>> with open_csv('spam.csv') as reader:  # doctest: +SKIP
    ...     assert list(reader) == [row]

    Raises:
        TypeError: With ``mode='w'`` and ``rowtype='dict'`` but missing ``fieldnames`` keyword argument.

    Notes:
        - The ``reader``/``writer`` yields/expects string values as :func:`py:unicode` strings (PY3: :class:`py3:str`).
        - The underlying opened file object is closed on leaving the ``with``-block.
        - If ``encoding=None`` is given, :func:`py:locale.getpreferredencoding` is used.
        - Under Python 2, an optimized implementation is used for 8-bit encodings
          that are ASCII-compatible (e.g. the default ``'utf-8'``).
    """
    try:
        open_func = _OPEN_FUNCS[mode]
    except (KeyError, TypeError):
        raise ValueError('invalid mode: %r' % mode)
    return open_func(filename, encoding, dialect, rowtype, **fmtparams)


def iterrows(filename, encoding=ENCODING, dialect=DIALECT,
             rowtype=ROWTYPE, **fmtparams):
    r"""Iterator yielding rows from a CSV file (closed on exaustion or error).

    Args:
        filename: File (name) argument for the :func:`py:io.open` call.
        encoding (str): Name of the encoding used to decode the file content.
        dialect: CSV dialect argument for :func:`csv23.reader`.
        rowtype (str):
            ``'list'`` for ``list`` rows,
            ``'dict'`` for :class:`py:dict` rows,
            ``'namedtuple'`` for :func:`py:collections.namedtuple` rows.
        \**fmtparams: Keyword arguments (formatting parameters) for the
            :func:`csv23.reader`.

    Yields:
        ``list``, :class:`py:dict`, or :func:`py:collections.namedtuple`:
        The next row from the CSV file.

    >>> for row in iterrows('spam.csv', encoding='utf-8'):  # doctest: +SKIP
    ...     print(row)
    ...     break
    [u'Wonderful Spam', u'Lovely Spam']

    >>> rows = iterrows('spam.csv', encoding='utf-8')  # doctest: +SKIP
    >>> next(rows)  # doctest: +SKIP
    [u'Wonderful Spam', u'Lovely Spam']
    >>> rows.close()  # doctest: +SKIP

    Notes:
        - The rows are ``list`` or :class:`py:dict` of :func:`py:unicode` strings (PY3: :class:`py3:str`).
        - The underlying opened file object is closed automatically, i.e.
          on exhaustion, in case of an exception, or by garbage collection.
          To do it manually, call the ``.close()``.method  of the returned generator object.
        - If ``encoding=None`` is given, :func:`py:locale.getpreferredencoding` is used.
        - Under Python 2, an optimized implementation is used for 8-bit encodings
          that are ASCII-compatible (e.g. the default ``'utf-8'``).
    """
    with open_reader(filename, encoding, dialect, rowtype, **fmtparams) as reader:
        for row in reader:
            yield row
