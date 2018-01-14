# readers.py - re/decoding csv.reader wrappers, convenience context manager

# TODO: consider open_reader(rowtype='OrderedDict') (Python 3.6 compat)

from __future__ import unicode_literals

import csv
import functools

__all__ = [
    'open_reader',
    'reader', 'DictReader',
    'UnicodeTextReader', 'UnicodeBytesReader',
]

from ._common import PY2, ENCODING, DIALECT, ROWTYPE
from ._common import none_encoding, is_8bit_clean, _open_csv
from ._dispatch import register_reader, get_reader
from ._workarounds import warn_if_issue31590


def open_reader(filename, encoding=ENCODING, dialect=DIALECT, rowtype=ROWTYPE, **fmtparams):
    r"""Context manager returning a CSV reader (closing the file on exit).

    Args:
        filename: File (name) argument for the :func:`py:io.open` call.
        encoding (str): Name of the encoding used to decode the file content.
        dialect: Dialect argument for the :func:`py:csv.reader`.
        rowtype (str): ``'list'`` for a :func:`py:csv.reader`,
           ``'dict'`` for a :class:`py:csv.DictReader`.
        \**fmtparams: Keyword arguments (formatting parameters) for the
            :func:`py:csv.reader`.

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
        - The reader yields a ``list`` or ``dict`` of ``unicode`` strings (PY3: ``str``).
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


def reader(stream, dialect=DIALECT, encoding=False, **fmtparams):
    r"""CSV reader yielding lists of ``unicode`` strings (PY3: ``str``).

    Args:
        stream: Iterable of text (``unicode``, PY3: ``str``) lines. If an
            ``encoding`` is given, iterable of encoded (``str``, PY3: ``bytes``)
            lines in the given (8-bit clean) ``encoding``.
        dialect: Dialect argument for the :func:`py:csv.reader`.
        encoding: If not ``False`` (default): name of the encoding needed to
            decode the encoded (``str``, PY3: ``bytes``) lines from ``stream``.
        \**fmtparams: Keyword arguments (formatting parameters) for the
            :func:`py:csv.reader`.

    Returns:
        A Python 3 :func:`py3:csv.reader` stand-in yielding a list of ``unicode`` strings
        (PY3: ``str``) for each row.

    >>> import io
    >>> text = u'Spam!,Spam!,Spam!\r\nSpam!,Lovely Spam!,Lovely Spam!\r\n'
    >>> with io.StringIO(text, newline='') as f:
    ...     for row in reader(f):
    ...         print(', '.join(row))
    Spam!, Spam!, Spam!
    Spam!, Lovely Spam!, Lovely Spam!

    Raises:
        NotImplementedError: If ``encoding`` is not 8-bit clean.
    """
    if encoding is False:
        return UnicodeTextReader(stream, dialect, **fmtparams)
    if encoding is None:
        encoding = none_encoding()
    if not is_8bit_clean(encoding):
        raise NotImplementedError
    return UnicodeBytesReader(stream, dialect, encoding, **fmtparams)


@register_reader('dict', 'text')
@register_reader('dict', 'bytes')
class DictReader(csv.DictReader):
    """:func:`csv23.reader` yielding dicts of ``unicode`` strings (PY3: ``str``)."""

    def __init__(self, f, fieldnames=None, restkey=None, restval=None, dialect=DIALECT, encoding=False, **kwds):
        # NOTE: csv.DictReader is an old-style class on PY2
        csv.DictReader.__init__(self, [], fieldnames, restkey, restval)
        self.reader = reader(f, dialect, encoding, **kwds)


class Reader(object):
    """Proxy for csv.reader."""

    def __init__(self, stream, dialect=DIALECT, **kwargs):
        self._reader = csv.reader(stream, dialect, **kwargs)
        warn_if_issue31590(self._reader)

    def __iter__(self):
        return self

    @property
    def dialect(self):
        return self._reader.dialect

    @property
    def line_num(self):
        return self._reader.line_num


class UnicodeReader(Reader):
    """CSV reader yielding lists of ``unicode`` strings (PY3: ``str``)."""

    if PY2:
        def next(self):
            return map(self._decode, self._reader.next())
    else:
        def __next__(self):
            return next(self._reader)


if PY2:
    @register_reader('list', 'text')
    class UnicodeTextReader(UnicodeReader):
        """Unicode CSV reader for iterables of text (``unicode``) lines."""

        def __init__(self, stream, dialect=DIALECT, **kwargs):
            bytes_stream = (line.encode('utf-8') for line in stream)
            super(UnicodeTextReader, self).__init__(bytes_stream, dialect, **kwargs)
            self._decode = lambda s: unicode(s, 'utf-8')


    @register_reader('list', 'bytes')
    class UnicodeBytesReader(UnicodeReader):
        """Unicode CSV reader for iterables of 8-bit clean encoded (``str``) lines."""

        def __init__(self, stream, dialect=DIALECT, encoding=ENCODING, **kwargs):
            super(UnicodeBytesReader, self).__init__(stream, dialect, **kwargs)
            self._decode = lambda s: unicode(s, encoding)

else:
    #: Unicode CSV reader for iterables of text (``str``) lines.
    UnicodeTextReader = csv.reader
    register_reader('list', 'text')(UnicodeTextReader)


    @register_reader('list', 'bytes')
    class UnicodeBytesReader(UnicodeReader):
        """Unicode CSV reader for iterables of 8-bit clean encoded (``bytes``) lines."""
        def __init__(self, stream, dialect=DIALECT, encoding=ENCODING, **kwargs):
            text_stream = (str(line, encoding) for line in stream)
            super(UnicodeBytesReader, self).__init__(text_stream, dialect, **kwargs)
