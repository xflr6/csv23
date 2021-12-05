"""Convenience context managers."""

# TODO: consider open_reader(rowtype='OrderedDict') (Python 3.6 compat)

from __future__ import unicode_literals

import contextlib
import functools
import io

from ._common import (PY2, ENCODING, DIALECT, ROWTYPE,
                      none_encoding, is_8bit_clean)
from ._dispatch import get_reader, get_writer

__all__ = ['open_reader', 'open_writer']


def open_reader(filename, encoding=ENCODING, dialect=DIALECT, rowtype=ROWTYPE, **fmtparams):
    r"""Context manager returning a CSV reader (closing the file on exit).

    Args:
        filename: File (name) argument for the :func:`py:io.open` call.
        encoding (str): Name of the encoding used to decode the file content.
        dialect: Dialect argument for the :func:`csv23.reader`.
        rowtype (str): ``'list'`` for a :func:`csv23.reader`,
           ``'dict'`` for a :class:`csv23.DictReader`,
           ``'namedtuple'`` for a :class:`csv23.NamedTupleReader`.
        \**fmtparams: Keyword arguments (formatting parameters) for the
            :func:`csv23.reader`.

    Returns:
        A context manager returning a Python 3 :func:`py3:csv.reader` stand-in when entering.

    >>> with open_reader('spam.csv', encoding='utf-8') as reader:  # doctest: +SKIP
    ...     for row in reader:
    ...         print(row)
    [u'Spam!', u'Spam!', u'Spam!']
    [u'Spam!', u'Lovely Spam!', u'Lovely Spam!']
    >>> reader.line_num  # doctest: +SKIP
    2

    Notes:
        - The reader yields a ``list`` or :class:`py:dict` of :func:`py:unicode` strings (PY3: :class:`py3:str`).
        - The underlying opened file object is closed on leaving the ``with``-block.
        - If ``encoding=None`` is given, :func:`py:locale.getpreferredencoding` is used.
        - Under Python 2, an optimized implementation is used for 8-bit encodings
          that are ASCII-compatible (e.g. the default ``'utf-8'``).
    """
    if encoding is None:
        encoding = none_encoding()
    if PY2 and is_8bit_clean(encoding):  # avoid recoding
        open_kwargs = {'mode': 'rb'}
        reader_func = get_reader(rowtype, 'bytes')
        reader_func = functools.partial(reader_func, encoding=encoding)
    else:
        open_kwargs = {'mode': 'r', 'encoding': encoding, 'newline': ''}
        reader_func = get_reader(rowtype, 'text')
    return _open_csv(filename, open_kwargs, reader_func, dialect, fmtparams)


def open_writer(filename, encoding=ENCODING, dialect=DIALECT, rowtype=ROWTYPE, **fmtparams):
    r"""Context manager returning a CSV writer (closing the file on exit).

    Args:
        filename: File (name) argument for the :func:`py:io.open` call.
        encoding (str): Name of the encoding used to encode the output lines.
        dialect: Dialect argument for the :func:`csv23.writer`.
        rowtype (str): ``'list'`` for a :func:`csv23.writer`,
            ``'dict'`` for a :class:`csv23.DictWriter`,
            ``'namedtuple'`` for a :class:`csv23.NamedTupleWriter`.
        \**fmtparams: Keyword arguments (formatting parameters) for the
            :func:`csv23.writer` (must include ``fieldnames`` with
            ``rowtype='dict'``).

    Returns:
        A context manager returning a Python 3 :func:`py3:csv.writer` stand-in when entering.

    >>> with open_writer('spam.csv', encoding='utf-8') as writer:  # doctest: +SKIP
    ...     writer.writerow([u'Spam!', u'Spam!', u'Spam!'])
    ...     writer.writerow([u'Spam!', u'Lovely Spam!', u'Lovely Spam!'])

    Raises:
        TypeError: With ``rowtype='dict'`` but missing ``fieldnames`` keyword argument.

    Notes
        - The writer expects string values as :func:`py:unicode` strings (PY3: :class:`py3:str`).
        - The underlying opened file object is closed on leaving the ``with``-block.
        - If ``encoding=None`` is given, :func:`py:locale.getpreferredencoding` is used.
        - Under Python 2, an optimized implementation is used for 8-bit encodings
          that are ASCII-compatible (e.g. the default ``'utf-8'``).
    """
    if encoding is None:
        encoding = none_encoding()
    if PY2 and is_8bit_clean(encoding):  # avoid recoding
        open_kwargs = {'mode': 'wb'}
        writer_func = get_writer(rowtype, 'bytes')
        writer_func = functools.partial(writer_func, encoding=encoding)
    else:
        open_kwargs = {'mode': 'w', 'encoding': encoding, 'newline': ''}
        writer_func = get_writer(rowtype, 'text')
    if rowtype == 'dict' and 'fieldnames' not in fmtparams:
        raise TypeError("open_writer(rowtype='dict') requires a 'fieldnames' "
                        "keyword argument to be passed to csv.DictWriter")
    return _open_csv(filename, open_kwargs, writer_func, dialect, fmtparams)


@contextlib.contextmanager
def _open_csv(filename, open_kwargs, csv_func, dialect, reader_kwargs):
    """io.open() context manager returning csv_func(<file>, dialect=dialect)."""
    f = io.open(filename, **open_kwargs)
    try:
        yield csv_func(f, dialect=dialect, **reader_kwargs)
    finally:
        f.close()
