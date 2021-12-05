"""collections.namedtuple reader/writer."""

from __future__ import unicode_literals

import collections

from ._common import PY2, DIALECT, lazyproperty
from ._dispatch import register_reader, register_writer
from . import readers
from . import writers

__all__ = ['NamedTupleReader', 'NamedTupleWriter']

ROW_NAME = 'Row'


@register_reader('namedtuple', 'bytes', 'text')
class NamedTupleReader(object):
    r""":func:`csv23.reader` yielding namedtuples of :func:`py:unicode` strings (PY3: :class:`py3:str`).

    Args:
        stream: Iterable of text (:func:`py:unicode`, PY3: :class:`py3:str`) lines.
            If an ``encoding`` is given, iterable of encoded (:class:`py:str`, PY3: :class:`py3:bytes`)
            lines in the given (8-bit clean) ``encoding``.
        dialect: Dialect argument for the :func:`csv23.reader`.
        rename: rename argument for :func:`py:collections.namedtuple`, or a
            function that is mapped to the first row to turn it into the
            ``field_names`` of the namedtuple.
        row_name: The ``typename`` for the row :func:`py:collections.namedtuple`.
        encoding: If not ``False`` (default): name of the encoding needed to
            decode the encoded (:class:`py:str`, PY3: :class:`py3:bytes`) lines from ``stream``.
        \**kwargs: Keyword arguments for the :func:`csv23.reader`.

    Raises:
        NotImplementedError: If ``encoding`` is not 8-bit clean.

    Notes:
        - Creates a :func:`py:collections.namedtuple` when reading the first row (header).
        - Uses the first row as ``field_names``. They must be valid Python identifiers
          (e.g. no hyphen or dot, they cannot be Python keywords like `class`).
          They cannot start with an underscore.
        - ``rename=True`` replaces invalid ``field_names`` with positional names (``_0``, ``_1``, etc.).
        - If ``rename`` is callable, it is applied to turn the first row strings into ``field_names``.

    >>> import io
    >>> text = u'coordinate.x,coordinate.y\r\n11,22\r\n'
    >>> with io.StringIO(text, newline='') as f:
    ...     for row in NamedTupleReader(f, rename=lambda x: x.replace('.', '_')):
    ...         print('%s %s' % (row.coordinate_x, row.coordinate_y))
    11 22
    """

    def __init__(self, stream, dialect=DIALECT, rename=False, row_name=ROW_NAME,
                 encoding=False, **kwargs):
        self._reader = readers.reader(stream, dialect, encoding, **kwargs)
        self._rename = rename
        self._row_name = row_name
        self._row_cls = None

    def __iter__(self):
        return self

    def __next__(self):
        """Return the next row of the reader's iterable object as a namedtuple,
        parsed according to the current dialect.
        Usually you should call this as next(reader)."""
        make_row = self._make_row
        return make_row(next(self._reader))

    if PY2:
        next = __next__
        del __next__

    @lazyproperty
    def _make_row(self):
        assert self._row_cls is None
        try:
            header = next(self._reader)
        except StopIteration:
            raise RuntimeError('missing header line for namedtuple fields')
        if callable(self._rename):
            header = map(self._rename, header)
            rename = False
        else:
            rename = self._rename
        self._row_cls = collections.namedtuple(self._row_name, header, rename=rename)
        return self._row_cls._make

    @property
    def dialect(self):
        """A read-only description of the dialect in use by the parser."""
        return self._reader.dialect

    @property
    def line_num(self):
        """The number of lines read from the source iterator.
        This is not the same as the number of records returned,
        as records can span multiple lines."""
        return self._reader.line_num

    @property
    def row_cls(self):
        """The row tuple subclass from :func:`py:collections.namedtuple` (``None`` before the first row is read)."""
        return self._row_cls


@register_writer('namedtuple', 'bytes', 'text')
class NamedTupleWriter(object):
    r""":func:`csv23.writer` for namedtuples where string values are :func:`py:unicode` strings (PY3: :class:`py3:str`).

    Args:
        stream: File-like object (in binary mode if ``encoding`` is given).
        dialect: Dialect argument for the func:`csv23.writer`.
        encoding: If not ``False`` (default): name of the encoding used to
            encode the output lines.
        \**kwargs: Keyword arguments for the :func:`csv23.writer`.

    Raises:
        NotImplementedError: If ``encoding`` is not 8-bit clean.
    """

    def __init__(self, stream, dialect=DIALECT, encoding=False, **kwargs):
        self._writer = writers.writer(stream, dialect, encoding, **kwargs)

    def writerow(self, row):
        """Write the row namedtuple to the writer's file object,
        formatted according to the current dialect."""
        self._writer.writerow(row._fields)
        self._writer.writerow(row)
        self.writerow = self._writer.writerow

    def writerows(self, rows):
        """Write all the rows namedtuples to the writer's file object,
        formatted according to the current dialect."""
        for r in rows:
            self.writerow(r)

    @property
    def dialect(self):
        """A read-only description of the dialect in use by the writer."""
        return self._writer.dialect
