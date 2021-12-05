"""Re/encoding csv.writer wrappers."""

from __future__ import unicode_literals

import csv
import io

from ._common import (PY2, ENCODING, DIALECT,
                      none_encoding, is_8bit_clean, csv_args)
from ._dispatch import register_writer
from ._workarounds import has_issue12178

if PY2:
    import mock
else:
    from unittest import mock

__all__ = ['writer', 'DictWriter',
           'UnicodeTextWriter', 'UnicodeBytesWriter']


def writer(stream, dialect=DIALECT, encoding=False, **fmtparams):
    r"""CSV writer for rows where string values are :func:`py:unicode` strings (PY3: :class:`py3:str`).

    Args:
        stream: File-like object (in binary mode if ``encoding`` is given).
        dialect: Dialect argument for the underlying :func:`py:csv.writer`.
        encoding: If not ``False`` (default): name of the encoding used to
            encode the output lines.
        \**fmtparams: Keyword arguments (formatting parameters) for the
            underlying :func:`py:csv.writer`.

    Returns:
        A Python 3 :func:`py3:csv.writer` stand-in taking  a list of :func:`py:unicode` strings
        (PY3: :class:`py3:str`) for each row.

    >>> import io
    >>> with io.StringIO(newline='') as f:  # doctest: +SKIP
    ...     w = writer(f)
    ...     w.writerow([u'Wonderful Spam', u'Lovely Spam'])
    ...     w.writerow([u'Spam!', u'Spam!', u'Spam!'])
    ...     f.getvalue()
    u'Spam!,Spam!,Spam!\r\nWonderful Spam,Lovely Spam\r\n'

    Raises:
        NotImplementedError: If ``encoding`` is not 8-bit clean.
    """
    if encoding is False:
        return UnicodeTextWriter(stream, dialect, **fmtparams)
    if encoding is None:
        encoding = none_encoding()
    if not is_8bit_clean(encoding):
        raise NotImplementedError
    return UnicodeBytesWriter(stream, dialect, encoding, **fmtparams)


@register_writer('dict', 'bytes', 'text')
class DictWriter(csv.DictWriter):
    """:func:`csv23.writer` for dicts where string values are :func:`py:unicode` strings (PY3: :class:`py3:str`)."""

    def __init__(self, f, fieldnames, restval='', extrasaction='raise',
                 dialect=DIALECT, encoding=False, **kwds):
        # NOTE: csv.DictWrier is an old-style class on PY2
        csv.DictWriter.__init__(self, mock.mock_open()(), fieldnames, restval,
                                extrasaction)
        self.writer = writer(f, dialect, encoding, **kwds)


class Writer(object):
    """Proxy for ``csv.writer``."""

    def __init__(self, stream, dialect=DIALECT, **kwargs):
        self._writer = csv.writer(stream, dialect, **kwargs)
        if has_issue12178(self._writer.dialect):
            self.writerow = wrapped_writerow(self.writerow,
                                             self._writer.dialect.escapechar)

    @property
    def dialect(self):
        return self._writer.dialect


def wrapped_writerow(method, escapechar, type_=unicode if PY2 else str):
    old, new = escapechar, escapechar * 2

    def writerow_func(row):
        row = [s.replace(old, new) if isinstance(s, type_) else s for s in row]
        return method(row)

    return writerow_func


class UnicodeWriter(Writer):
    """CSV writer for rows where string values are :func:`py:unicode` strings (PY3: :class:`py3:str`)."""

    if PY2:
        def __init__(self, stream, dialect=DIALECT, **kwargs):
            kwargs = csv_args(kwargs)
            super(UnicodeWriter, self).__init__(stream, dialect, **kwargs)

    def writerows(self, rows):
        for r in rows:
            self.writerow(r)


if PY2:
    @register_writer('list', 'text')
    class UnicodeTextWriter(UnicodeWriter):
        """Unicode CSV writer for writing text (``unicode``) lines."""

        def __init__(self, stream, dialect=DIALECT, **kwargs):
            self._buffer = io.BytesIO()
            super(UnicodeTextWriter, self).__init__(self._buffer, dialect, **kwargs)
            self._stream = stream

        def writerow(self, row):
            row = [v.encode('utf-8') if isinstance(v, unicode) else v
                   for v in row]
            self._writer.writerow(row)
            line = unicode(self._buffer.getvalue(), 'utf-8')
            # NOTE: self._buffer.truncate(0) would prepend zero-bytes
            self._buffer.seek(0)
            self._buffer.truncate()
            return self._stream.write(line)


    @register_writer('list', 'bytes')
    class UnicodeBytesWriter(UnicodeWriter):
        """Unicode CSV writer for writing 8-bit clean encoded (``str``) lines."""

        def __init__(self, stream, dialect=DIALECT, encoding=ENCODING, **kwargs):
            super(UnicodeBytesWriter, self).__init__(stream, dialect, **kwargs)
            self._encoding = encoding

        def writerow(self, row):
            row = [v.encode(self._encoding) if isinstance(v, unicode) else v for v in row]
            return self._writer.writerow(row)


else:
    @register_writer('list', 'text')
    def UnicodeTextWriter(stream, dialect=DIALECT, **kwargs):  # noqa: N802
        """Unicode CSV writer for writing text (``str``) lines."""
        writer = csv.writer(stream, dialect, **kwargs)
        if has_issue12178(writer.dialect):
            return _UnicodeTextWriter(stream, dialect, **kwargs)
        return writer


    class _UnicodeTextWriter(UnicodeWriter):
        __doc__ = UnicodeTextWriter.__doc__

        def writerow(self, row):
            return self._writer.writerow(row)


    @register_writer('list', 'bytes')
    class UnicodeBytesWriter(UnicodeWriter):
        """Unicode CSV writer for writing 8-bit clean encoded (``bytes``) lines."""

        def __init__(self, stream, dialect=DIALECT, encoding=ENCODING, **kwargs):
            self._buffer = io.StringIO(newline='')
            super(UnicodeBytesWriter, self).__init__(self._buffer, dialect, **kwargs)
            self._stream = stream
            self._encoding = encoding

        def writerow(self, row):
            self._writer.writerow(row)
            line = self._buffer.getvalue().encode(self._encoding)
            # NOTE: self._buffer.truncate(0) would prepend zero-bytes
            self._buffer.seek(0)
            self._buffer.truncate()
            return self._stream.write(line)
