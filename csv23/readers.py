"""Re/decoding csv.reader wrappers, convenience context manager."""

import csv

from ._common import ENCODING, DIALECT, none_encoding, is_8bit_clean
from ._dispatch import register_reader

__all__ = ['reader', 'DictReader',
           'UnicodeTextReader', 'UnicodeBytesReader']


def reader(stream, dialect=DIALECT, encoding=False, **fmtparams):
    r"""CSV reader yielding lists of :func:`py:unicode` strings (PY3: :class:`py3:str`).

    Args:
        stream: Iterable of text (:func:`py:unicode`, PY3: :class:`py3:str`) lines.
            If an ``encoding`` is given, iterable of encoded (:class:`py:str`, PY3: :class:`py3:bytes`)
            lines in the given (8-bit clean) ``encoding``.
        dialect: Dialect argument for the underlying :func:`py:csv.reader`.
        encoding: If not ``False`` (default): name of the encoding needed to
            decode the encoded (:class:`py:str`, PY3: :class:`py3:bytes`) lines from ``stream``.
        \**fmtparams: Keyword arguments (formatting parameters) for the
            underlying :func:`py:csv.reader`.

    Returns:
        A Python 3 :func:`py3:csv.reader` stand-in yielding a list of :func:`py:unicode` strings
        (PY3: :class:`py3:str`) for each row.

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


@register_reader('dict', 'bytes', 'text')
class DictReader(csv.DictReader):
    """:func:`csv23.reader` yielding dicts of :func:`py:unicode` strings (PY3: :class:`py3:str`)."""

    def __init__(self, f, fieldnames=None, restkey=None, restval=None,
                 dialect=DIALECT, encoding=False, **kwds):
        super().__init__([], fieldnames, restkey, restval)
        self.reader = reader(f, dialect, encoding, **kwds)


class Reader(object):
    """Proxy for ``csv.reader``."""

    def __init__(self, stream, dialect=DIALECT, **kwargs):
        self._reader = csv.reader(stream, dialect, **kwargs)

    def __iter__(self):
        return self

    @property
    def dialect(self):
        return self._reader.dialect

    @property
    def line_num(self):
        return self._reader.line_num


class UnicodeReader(Reader):
    """CSV reader yielding lists of :func:`py:unicode` strings (PY3: :class:`py3:str`)."""

    def __next__(self):
        return next(self._reader)


#: Unicode CSV reader for iterables of text (``str``) lines.
UnicodeTextReader = csv.reader
register_reader('list', 'text')(UnicodeTextReader)


@register_reader('list', 'bytes')
class UnicodeBytesReader(UnicodeReader):
    """Unicode CSV reader for iterables of 8-bit clean encoded (``bytes``) lines."""
    def __init__(self, stream, dialect=DIALECT, encoding=ENCODING, **kwargs):
        text_stream = (str(line, encoding) for line in stream)
        super(UnicodeBytesReader, self).__init__(text_stream, dialect, **kwargs)
