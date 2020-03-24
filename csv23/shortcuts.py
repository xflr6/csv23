# shortcuts.py - overloaded functions

import functools
import io
import itertools
import sys

from . import (DIALECT,
               ENCODING,
               writer as csv23_writer)

__all__ = ['read_csv', 'write_csv']

def iterslices(iterable, size):
    iterable = iter(iterable)
    next_slice = functools.partial(itertools.islice, iterable, size)
    return iter(lambda: list(next_slice()), [])


def read_csv(filename, dialect=DIALECT, encoding=ENCODING):
    raise NotImplementedError


if sys.version_info.major == 2:
    def write_csv(filename, rows, header=None, dialect=DIALECT,
                  encoding=ENCODING):
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
            f = nullcontext(f)
        elif hasattr(filename, 'hexdigest'):
            result = filename
            assert encoding is not None
            f = io.TextIOWrapper(io.BytesIO(), **textio_kwargs)
            hash_ = filename
        else:
            result = pathlib.Path(filename)
            assert encoding is not None
            f = open(str(filename), 'wt', **open_kwargs)

        with f as f:
            writer = csv23_writer(f, dialect=dialect, encoding=False)

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
