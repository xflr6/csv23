"""Overloaded functions (Python 3 only)."""

import functools
import io
import itertools
import sys
import warnings

from ._common import PY2

from . import (DIALECT, ENCODING,
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
    def read_csv(file, dialect=DIALECT, encoding=ENCODING, as_list=False,
                 autocompress=False):
        """Iterator yielding rows from a file-like object with CSV data."""
        raise NotImplementedError('Python 3 only')


    def write_csv(file, rows, header=None, dialect=DIALECT, encoding=ENCODING,
                  autocompress=False):
        """Write rows into a file-like object using CSV format."""
        raise NotImplementedError('Python 3 only')


else:
    import operator
    import pathlib
    import platform
    from contextlib import nullcontext

    # workaround https://foss.heptapod.net/pypy/pypy/issues/3217
    _get_update_bytes = (operator.methodcaller('getvalue')
                         if platform.python_implementation() == 'PyPy' else
                         operator.methodcaller('getbuffer'))

    import builtins, bz2, gzip, lzma

    SUFFIX_OPEN_MODULE = {'.bz2':  bz2,
                          '.gz': gzip,
                          '.xz': lzma}


    def _get_open_module(filepath, autocompress=False):
        suffix = ''.join(filepath.rpartition('.')[1:]).lower()
        if autocompress:
            result = SUFFIX_OPEN_MODULE.get(suffix, builtins)
        else:
            result = builtins
            if suffix in SUFFIX_OPEN_MODULE:
                msg = 'fille %r has suffix %r but autocompress=False' % (filepath, suffix)
                warnings.warn(msg)
        return result


    def read_csv(file, dialect=DIALECT, encoding=ENCODING, as_list=False,
                 autocompress=False):
        r"""Iterator yielding rows from a file-like object with CSV data.

        Args:
            file: Source as readable file-like object or filename/:class:`py:os.PathLike`.
            dialect: CSV dialect argument for the :func:`csv23.reader`.
            encoding (str): Name of the encoding used to decode the file content.
            as_list (bool): Return a :class:`py:list` of rows instead of an iterator.
            autocompress(bool): Decompress if ``file`` is a path that ends in
                ``'.bz2'``, ``'.gz'``, or ``'.xz'``.

        Returns:
            An iterator yielding a :class:`py:list` of row values for each row.

        >>> read_csv(io.BytesIO(b'spam,eggs\r\n'), encoding='ascii', as_list=True)
        [['spam', 'eggs']]

        Raises:
            TypeError: If ``file`` is a binary buffer or filename/path
                and ``encoding`` is ``None``. Also if ``file`` is a text buffer
                and ``encoding`` is not ``None``.

        Warns:
            UserWarning: If file is a path that ends in
                ``'.bz2'``, ``'.gz'``, or ``'.xz'`` but ``autocompress=False`` is given.

        Notes:
            - ``encoding`` is required if ``file`` is binary or a filesystem path.
            - if ``file`` is a text stream, ``encoding`` needs to be ``None``.
        """
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
            filepath = str(file)
            open_module = _get_open_module(filepath, autocompress=autocompress)
            f = open_module.open(filepath, 'rt', **open_kwargs)

        rows = iterrows(f, dialect=dialect)
        if as_list:
            rows = list(rows)
        return rows


    def write_csv(file, rows, header=None, dialect=DIALECT, encoding=ENCODING,
                  autocompress=False):
        r"""Write rows into a file-like object using CSV format.

        Args:
            file: Target as writeable file-like object, or as filename
                or :class:`py:os.Pathlike`, or as updateable hash,
                or ``None`` for string output.
            rows: CSV values to write as iterable of row value iterables.
            header: Iterable of first row values or ``None`` for no header.
            dialect: Dialect argument for the :func:`csv23.writer`.
            encoding (str): Name of the encoding used to encode the file content.
            autocompress(bool): Compress if ``file`` is a path that ends in
                ``'.bz2'``, ``'.gz'``, or ``'.xz'``.

        Returns:
            If ``file`` is a filename/path, return it as :class:`py:pathlib.Path`.
            If ``file`` is a file-like object or a hash return it (without closing).
            If ``file`` is ``None`` return the CSV data as :class:`py:str`.

        >>> write_csv(io.BytesIO(), iter([('spam', 'eggs')]), encoding='ascii').getvalue()
        b'spam,eggs\r\n'

        Raises:
            TypeError: If ``file`` is a binary buffer or filename/path
                and ``encoding`` is ``None``. Also if ``file`` is a text buffer
                and ``encoding`` is not ``None``.

        Warns:
            UserWarning: If file is a path that ends in
                ``'.bz2'``, ``'.gz'``, or ``'.xz'`` but ``autocompress=False`` is given.

        Notes:
            - ``encoding`` is required if ``file`` is binary or a filesystem path.
            - if ``file`` is a text stream, ``encoding`` needs to be ``None``.
        """
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
            filepath = str(file)
            open_module = _get_open_module(filepath, autocompress=autocompress)
            f = open_module.open(filepath, 'wt', **open_kwargs)

        with f as f:
            writer = csv23_writer(f, dialect=dialect, encoding=False)

            if header is not None:
                writer.writerows([header])

            if hashsum is not None:
                buf = f.buffer
                for rows in iterslices(rows, 1000):
                    writer.writerows(rows)
                    hashsum.update(_get_update_bytes(buf))
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
