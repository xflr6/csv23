# extras.py - namedtuple reader/writer

# TODO: document rename argument

from __future__ import unicode_literals

import collections

from ._common import PY2, DIALECT, lazyproperty
from ._dispatch import register_reader, register_writer
from . import readers, writers

__all__ = ['NamedTupleReader', 'NamedTupleWriter']


@register_reader('namedtuple', 'bytes', 'text')
class NamedTupleReader(object):
    """:func:`csv23.reader` yielding namedtuples of ``unicode`` strings (PY3: ``str``)."""

    def __init__(self, stream, dialect=DIALECT, rename=False, row_name='Row',
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
        #del __next__

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
        return self._row_cls


@register_writer('namedtuple', 'bytes', 'text')
class NamedTupleWriter(object):
    """:func:`csv23.writer` for namedtuples where string values are ``unicode`` strings (PY3: ``str``)."""

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
