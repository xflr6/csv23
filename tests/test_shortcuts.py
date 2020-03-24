# test_writers.py

import contextlib
import functools
import hashlib
import io
import os
import sys
import zipfile

import pytest

if pytest.csv23.PY2:
    import argparse
    pathlib = argparse.Namespace(Path=lambda x: x)

else:
    import pathlib

    from csv23.shortcuts import read_csv, write_csv

ROWS = [(u'sp\xe4m', 'eggs')]


@pytest.csv23.py3only
def test_read_csv(filename='spam.csv', encoding='utf-8'):
    with pytest.raises(NotImplementedError):
        read_csv(filename, encoding=encoding)


@pytest.csv23.py3only
@pytest.mark.parametrize('filename, rows, header, encoding, expected', [
    (None, ROWS, None, 'utf-8', b'sp\xc3\xa4m,eggs\r\n'),
    (None, ROWS, None, None, u'sp\xe4m,eggs\r\n'),
    (None, ROWS, ['key', 'value'], None, u'key,value\r\nsp\xe4m,eggs\r\n'),
])
def test_write_csv_none(filename, rows, header, encoding, expected):
    result = write_csv(filename, rows, header=header, encoding=encoding)
    assert result == expected


@pytest.csv23.py3only
@pytest.mark.parametrize('rows, header, encoding, expected', [
    (ROWS, None, 'utf-8', b'sp\xc3\xa4m,eggs\r\n'),
    (ROWS, None, None, u'sp\xe4m,eggs\r\n'),
])
def test_write_csv_write(rows, header, encoding, expected):
    buf = io.StringIO() if encoding is None else io.BytesIO()
    result = write_csv(buf, rows, header=header, encoding=encoding)
    assert result is buf
    assert result.getvalue() == expected


@pytest.csv23.py3only
@pytest.mark.skipif(sys.version_info <  (3, 6), reason='unavailable in 3.5')
@pytest.mark.parametrize('rows, header, encoding, expected', [
    (ROWS, None, 'utf-8', b'sp\xc3\xa4m,eggs\r\n'),
])
def test_write_csv_zipfile(tmp_path, rows, header, encoding, expected):
    if sys.version_info < (3, 6):
        tmp_path = pathlib.Path(str(tmp_path))

    archive = tmp_path / 'spam.zip'
    filename = 'spam.csv'
    with zipfile.ZipFile(archive, 'w') as z,\
         z.open(filename, 'w') as f:
        result = write_csv(f, rows, header=header, encoding=encoding)

    assert result is f
    assert archive.exists()
    assert archive.stat().st_size
    with zipfile.ZipFile(archive) as z:
        assert z.namelist() == [filename]
        assert z.read(filename) == expected


@contextlib.contextmanager
def chdir(path):
    old = os.getcwd()
    os.chdir(str(path))
    try:
        yield None
    finally:
        os.chdir(old)


@pytest.csv23.py3only
@pytest.mark.parametrize('filename, rows, header, encoding, expected', [
    ('spam.csv', ROWS, None, 'utf-8', b'sp\xc3\xa4m,eggs\r\n'),
    (pathlib.Path('spam.csv'), ROWS, None, 'utf-8', b'sp\xc3\xa4m,eggs\r\n'),
    ('nonfilename', ROWS, None, None, None),
])
def test_write_csv_filename(tmp_path, filename, rows, header, encoding, expected):
    if sys.version_info < (3, 6):
        tmp_path = pathlib.Path(str(tmp_path))

    kwargs = {'header': header, 'encoding': encoding}

    if encoding is None:
        with pytest.raises(AssertionError):
            write_csv(filename, rows, **kwargs)
        return

    target = tmp_path / filename

    with chdir(tmp_path):
        result = write_csv(filename, rows, **kwargs)
        assert result.exists()
        assert target.exists()
        assert result.samefile(target)
        assert result.samefile(pathlib.Path(filename))

    assert target.stat().st_size
    assert target.read_bytes() == expected


@pytest.csv23.py3only
@pytest.mark.parametrize('rows, header, encoding, hash_name, expected', [
    (ROWS, None, 'utf-8', 'sha256', 'c793b37cb2008e5591d127db8232085e'
                                    '64944cae5315ca886f57988343f5b111'),
    (ROWS, None, 'utf-8', 'md5', '67bac4eb7cd16ea8eaf454eafa559d34'),
    (ROWS, None, 'utf-16', 'sha1', 'b0e0578b8149619569a4f56a3e6d05fed7de788f'),
])
def test_write_csv_hash(rows, header, encoding, hash_name, expected):
    hash_ = hashlib.new(hash_name)
    result = write_csv(hash_, rows, header=header, encoding=encoding)
    assert result is hash_
    assert result.hexdigest() == expected


@pytest.csv23.py3only
@pytest.mark.parametrize('rows, header, encoding, hash_name', [
    (ROWS, None, 'utf-8', 'sha256'),
    (ROWS, None, 'utf-16', 'sha1'),
])
def test_write_csv_equivalence(tmp_path, rows, header, encoding, hash_name):
    if sys.version_info < (3, 6):
        tmp_path = pathlib.Path(str(tmp_path))

    new = functools.partial(hashlib.new, hash_name)

    kwargs = {'header': header, 'encoding': encoding}

    r_hash = write_csv(new(), rows, **kwargs)

    r_none = write_csv(None, rows, **kwargs)
    r_write = write_csv(io.BytesIO(), rows, **kwargs).getvalue()
    r_filename = write_csv(tmp_path / 'spam.csv', rows, **kwargs).read_bytes()

    assert (r_hash.hexdigest()
            == new(r_none).hexdigest()
            == new(r_write).hexdigest()
            == new(r_filename).hexdigest())
