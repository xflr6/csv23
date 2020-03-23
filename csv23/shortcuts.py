# shortcuts.py - overloaded functions

import contextlib
import csv
import functools
import io
import itertools

from ._common import PY2

from . import DIALECT, ENCODING

__all__ = ['read_csv', 'write_csv']

def iterslices(iterable, size):
    iterable = iter(iterable)
    next_slice = functools.partial(itertools.islice, iterable, size)
    return iter(lambda: list(next_slice()), [])


def read_csv(filename, dialect=DIALECT, encoding=ENCODING):
    raise NotImplementedError


if PY2:
    def write_csv(filename, rows, header=None, dialect=DIALECT,
                  encoding=ENCODING):
        raise NotImplementedError('Python 3 only')
    
else:
    import pathlib

    def write_csv(filename, rows, header=None, dialect=DIALECT,
                  encoding=ENCODING):
        open_kwargs = {'encoding': encoding, 'newline': ''}
        textio_kwargs = dict(write_through=True, **open_kwargs)

        if filename is None:
            if encoding is None:
                f = io.StringIO()
            else:
                f = io.TextIOWrapper(io.BytesIO(), **textio_kwargs)
        elif hasattr(filename, 'write'):
            result = filename
            if encoding is None:
                f = filename
            else:
                f = io.TextIOWrapper(filename, **textio_kwargs)
            f = contextlib.nullcontext(f)
        elif hasattr(filename, 'hexdigest'):
            result = filename
            assert encoding is not None
            f = io.TextIOWrapper(io.BytesIO(), **textio_kwargs)
            hash_ = filename
        else:
            result = pathlib.Path(filename)
            assert encoding is not None
            f = open(filename, 'wt', **open_kwargs)

        with f as f:
            writer = csv.writer(f, dialect=dialect)

            if header is not None:
                writer.writerows([header])

            if hasattr(filename, 'hexdigest'):
                buf = f.buffer
                for rows in iterslices(rows, 1000):
                    writer.writerows(rows)
                    hash_.update(buf.getbuffer())
                    # NOTE: f.truncate(0) would prepend zero-bytes
                    f.seek(0)
                    f.truncate()
            else:
                writer.writerows(rows)

            if filename is None:
                if encoding is not None:
                    f = f.buffer
                result = f.getvalue()

        if hasattr(filename, 'write') and encoding is not None:
            f.detach()

        return result
