# test_writers.py

import contextlib
import functools
import hashlib
import io
import os
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
@pytest.mark.parametrize('rows, filename, encoding, expected', [
    (ROWS, None, 'utf-8', b'sp\xc3\xa4m,eggs\r\n'),
    (ROWS, None, None, u'sp\xe4m,eggs\r\n'),
])
def test_write_csv_none(rows, filename, encoding, expected):
    result = write_csv(filename, rows, encoding=encoding)
    assert result == expected


@pytest.csv23.py3only
@pytest.mark.parametrize('rows, encoding, expected', [
    (ROWS, 'utf-8', b'sp\xc3\xa4m,eggs\r\n'),
    (ROWS, None, u'sp\xe4m,eggs\r\n'),
])
def test_write_csv_write(rows, encoding, expected):
    buf = io.StringIO() if encoding is None else io.BytesIO()
    result = write_csv(buf, rows, encoding=encoding)
    assert result is buf
    assert result.getvalue() == expected


@pytest.csv23.py3only
@pytest.mark.parametrize('rows, encoding, expected', [
    (ROWS, 'utf-8', b'sp\xc3\xa4m,eggs\r\n'),
])
def test_write_csv_zipfile(tmp_path, rows, encoding, expected):
    archive = tmp_path / 'spam.zip'
    filename = 'spam.csv'
    with zipfile.ZipFile(archive, 'w') as z,\
         z.open(filename, 'w') as f:
        result = write_csv(f, rows, encoding=encoding)

    assert result is f
    assert archive.exists()
    assert archive.stat().st_size
    with zipfile.ZipFile(archive) as z:
        assert z.namelist() == [filename]
        assert z.read(filename) == expected


@contextlib.contextmanager
def chdir(path):
    old = os.getcwd()
    os.chdir(path)
    try:
        yield None
    finally:
        os.chdir(old)


@pytest.csv23.py3only
@pytest.mark.parametrize('filename, rows, encoding, expected', [
    ('spam.csv', ROWS, 'utf-8', b'sp\xc3\xa4m,eggs\r\n'),
    (pathlib.Path('spam.csv'), ROWS, 'utf-8', b'sp\xc3\xa4m,eggs\r\n'),
    ('nonfilename', ROWS, None, None),
])
def test_write_csv_filename(tmp_path, filename, rows, encoding, expected):
    if encoding is None:
        with pytest.raises(AssertionError):
            write_csv(filename, rows, encoding=encoding)
        return

    target = tmp_path / filename

    with chdir(tmp_path):
        result = write_csv(filename, rows, encoding=encoding)
        assert result.exists()
        assert target.exists()
        assert result.samefile(target)
        assert result.samefile(pathlib.Path(filename))

    assert target.stat().st_size
    assert target.read_bytes() == expected


@pytest.csv23.py3only
@pytest.mark.parametrize('rows, encoding, hash_name, expected', [
    (ROWS, 'utf-8', 'sha256', 'c793b37cb2008e5591d127db8232085e'
                              '64944cae5315ca886f57988343f5b111'),
    (ROWS, 'utf-8', 'md5', '67bac4eb7cd16ea8eaf454eafa559d34'),
    (ROWS, 'utf-16', 'sha1', 'b0e0578b8149619569a4f56a3e6d05fed7de788f'),
])
def test_write_csv_hash(rows, encoding, hash_name, expected):
    hash_ = hashlib.new(hash_name)
    result = write_csv(hash_, rows, encoding=encoding)
    assert result is hash_
    assert result.hexdigest() == expected


@pytest.csv23.py3only
@pytest.mark.parametrize('rows, encoding, hash_name', [
    (ROWS, 'utf-8', 'sha256'),
    (ROWS, 'utf-16', 'sha1'),
])
def test_write_csv_equivalence(tmp_path, rows, encoding, hash_name):
    new = functools.partial(hashlib.new, hash_name)

    r_hash = write_csv(new(), rows, encoding=encoding)

    r_none = write_csv(None, rows, encoding=encoding)
    r_write = write_csv(io.BytesIO(), rows, encoding=encoding).getvalue()
    r_filename = write_csv(tmp_path / 'spam.csv', rows, encoding=encoding).read_bytes()

    assert (r_hash.hexdigest()
            == new(r_none).hexdigest()
            == new(r_write).hexdigest()
            == new(r_filename).hexdigest())
