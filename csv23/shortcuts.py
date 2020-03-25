# shortcuts.py - overloaded functions (Python 3 only)

import functools
import io
import itertools
import sys

from ._common import PY2

from . import (DIALECT,
               ENCODING,
               reader as csv23_reader,
               writer as csv23_writer)

__all__ = ['read_csv', 'write_csv']


def iterslices(iterable, size):
    iterable = iter(iterable)
    next_slice = functools.partial(itertools.islice, iterable, size)
    return iter(lambda: list(next_slice()), [])


def iterrows(f, dialect=DIALECT):
    with f as _f:
        reader = csv23_reader(_f, dialect=dialect, encoding=False)
        for row in reader:
            yield row


if PY2:
    def read_csv(file, dialect=DIALECT, encoding=ENCODING, as_list=False):
        raise NotImplementedError('Python 3 only')

    def write_csv(file, rows, header=None, dialect=DIALECT, encoding=ENCODING):
        raise NotImplementedError('Python 3 only')
    
else:
    import pathlib

    if sys.version_info < (3, 7):
        import contextlib

        @contextlib.contextmanager
        def nullcontext(enter_result=None):
            yield enter_result

    else:
        from contextlib import nullcontext


    def read_csv(file, dialect=DIALECT, encoding=ENCODING, as_list=False):
        open_kwargs = {'encoding': encoding, 'newline': ''}

        if hasattr(file, 'read'):
            if isinstance(file, io.TextIOBase):
                if encoding is not None:
                    raise TypeError('bytes-like object expected')
                f = file
            else:
                if encoding is None:
                     raise TypeError('need encoding for wrapping byte-stream')
                f = io.TextIOWrapper(file, **open_kwargs)
            f = nullcontext(f)
        else:
            if encoding is None:
                raise TypeError('need encoding for opening file by path')
            f = open(str(file), 'rt', **open_kwargs)

        rows = iterrows(f, dialect=dialect)
        if as_list:
            rows = list(rows)
        return rows


    def write_csv(file, rows, header=None, dialect=DIALECT, encoding=ENCODING):
        open_kwargs = {'encoding': encoding, 'newline': ''}
        textio_kwargs = dict(write_through=True, **open_kwargs)

        hashsum = None

        if file is None:
            if encoding is None:
                f = io.StringIO()
            else:
                f = io.TextIOWrapper(io.BytesIO(), **textio_kwargs)
        elif hasattr(file, 'write'):
            result = file
            if encoding is None:
                f = file
            else:
                f = io.TextIOWrapper(file, **textio_kwargs)
            f = nullcontext(f)
        elif hasattr(file, 'hexdigest'):
            result = hashsum = file
            if encoding is None:
                raise TypeError('need encoding for wrapping byte-stream')
            f = io.TextIOWrapper(io.BytesIO(), **textio_kwargs)
        else:
            result = pathlib.Path(file)
            if encoding is None:
                raise TypeError('need encoding for opening file by path')
            f = open(str(file), 'wt', **open_kwargs)

        with f as f:
            writer = csv23_writer(f, dialect=dialect, encoding=False)

            if header is not None:
                writer.writerows([header])

            if hashsum is not None:
                buf = f.buffer
                for rows in iterslices(rows, 1000):
                    writer.writerows(rows)
                    hashsum.update(buf.getbuffer())
                    # NOTE: f.truncate(0) would prepend zero-bytes
                    f.seek(0)
                    f.truncate()
            else:
                writer.writerows(rows)

            if file is None:
                if encoding is not None:
                    f = f.buffer
                result = f.getvalue()

        if hasattr(file, 'write') and encoding is not None:
            f.detach()

        return result
