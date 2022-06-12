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

ROWS = [[u'sp\xe4m', 'eggs']]

STRING = u'sp\xe4m,eggs\r\n'

ENCODING = 'utf-8'

BYTES = b'sp\xc3\xa4m,eggs\r\n'

HEADER = ['key', 'value']

H_STRING = u'key,value\r\n'

H_BYTES = b'key,value\r\n'


@pytest.csv23.py2only
def test_read_csv_py2():
    with pytest.raises(NotImplementedError):
        read_csv('spam.csv', encoding='utf-8')


@pytest.csv23.py2only
def test_write_csv_py2():
    with pytest.raises(NotImplementedError):
        write_csv('spam.csv', ROWS, header=None, encoding='utf-8')


@pytest.mark.parametrize(
    'src, encoding, expected',
    [(BYTES, ENCODING, ROWS),
     (H_BYTES + BYTES, ENCODING, [HEADER] + ROWS),
     (BYTES, None, (TypeError, r'need encoding')),
     (STRING, None, ROWS),
     (H_STRING + STRING, None, [HEADER] + ROWS),
     (STRING, ENCODING, (TypeError, r'bytes-like object expected'))])
@pytest.csv23.py3only
def test_read_csv_iobase(tmp_path, src, encoding, expected):
    if sys.version_info < (3, 6):
        tmp_path = pathlib.Path(str(tmp_path))

    buf = (io.BytesIO if isinstance(src, bytes) else io.StringIO)(src)

    kwargs = {'encoding': encoding, 'as_list': True}

    if isinstance(expected, tuple):
        with pytest.raises(expected[0], match=expected[1]):
            read_csv(buf, **kwargs)
        return

    assert read_csv(buf, **kwargs) == expected

    source = tmp_path / 'spam.csv'
    if isinstance(buf, io.TextIOBase):
        assert encoding is None
        with source.open('wt', encoding='utf-8', newline='') as f:
            f.write(src)
        open_kwargs = {'mode': 'rt', 'encoding': 'utf-8', 'newline': ''}
        kwargs['encoding'] = None
    else:
        assert encoding is not None
        source.write_bytes(src)
        open_kwargs = {'mode': 'rb'}

    with source.open(**open_kwargs) as f:
        assert read_csv(f, **kwargs) == expected


@pytest.mark.parametrize(
    'raw, encoding, expected',
    [(BYTES, ENCODING, ROWS),
     (H_BYTES + BYTES, ENCODING, [HEADER] + ROWS),
     (BYTES, None, (TypeError, r'need encoding'))])
@pytest.csv23.py3only
def test_read_csv_filename(tmp_path, raw, encoding, expected):
    if sys.version_info < (3, 6):
        tmp_path = pathlib.Path(str(tmp_path))

    target = tmp_path / 'spam.csv'
    target.write_bytes(raw)

    kwargs = {'encoding': encoding, 'as_list': True}

    if isinstance(expected, tuple):
        with pytest.raises(expected[0], match=expected[1]):
            read_csv(target, **kwargs)
        return

    assert read_csv(target, **kwargs) == expected


@pytest.csv23.py3only  # unavailable in PY2
@pytest.mark.parametrize(
    'raw, encoding, expected',
    [(BYTES, ENCODING, ROWS),
     (H_BYTES + BYTES, ENCODING, [HEADER] + ROWS),
     (BYTES, None, (TypeError, r'need encoding'))])
def test_read_csv_zipfile(tmp_path, raw, encoding, expected):
    if sys.version_info < (3, 6):
        tmp_path = pathlib.Path(str(tmp_path))

    archive = tmp_path / 'spam.zip'
    filename = 'spam.csv'
    with zipfile.ZipFile(archive, 'w') as z,\
         z.open(filename, 'w') as f:
        f.write(raw)

    assert archive.exists()
    assert archive.stat().st_size

    kwargs = {'encoding': encoding, 'as_list': True}

    with zipfile.ZipFile(archive) as z,\
         z.open(filename) as f:
        assert z.namelist() == [filename]
        z.read(filename) == raw
        if isinstance(expected, tuple):
            assert encoding is None
            with pytest.raises(expected[0], match=expected[1]):
                read_csv(f, **kwargs)
            return

        assert read_csv(f, **kwargs) == expected


@pytest.csv23.py3only
@pytest.mark.parametrize(
    'rows, header, encoding, expected',
    [(ROWS, None, ENCODING, BYTES),
     (ROWS, HEADER, ENCODING, H_BYTES + BYTES),
     (ROWS, None, None, STRING),
     (ROWS, HEADER, None, H_STRING + STRING)])
def test_write_csv_none(rows, header, encoding, expected):
    result = write_csv(None, rows, header=header, encoding=encoding)
    assert result == expected


@pytest.csv23.py3only
@pytest.mark.parametrize(
    'rows, header, encoding, expected',
    [(ROWS, None, ENCODING, BYTES),
     (ROWS, HEADER, ENCODING, H_BYTES + BYTES),
     (ROWS, None, None, STRING),
     (ROWS, HEADER, None, H_STRING + STRING)])
def test_write_csv_write(rows, header, encoding, expected):
    buf = io.StringIO() if encoding is None else io.BytesIO()
    result = write_csv(buf, rows, header=header, encoding=encoding)
    assert result is buf
    assert result.getvalue() == expected


@pytest.csv23.py3only  # unavailable in PY2
@pytest.mark.parametrize(
    'rows, header, encoding, expected',
    [(ROWS, None, ENCODING, BYTES),
     (ROWS, HEADER, ENCODING, H_BYTES + BYTES),
     (ROWS, None, None, (TypeError,
                         (r'bytes-like object is required'
                          r'|does not support the buffer interface')))])
def test_write_csv_zipfile(tmp_path, rows, header, encoding, expected):
    if sys.version_info < (3, 6):
        tmp_path = pathlib.Path(str(tmp_path))

    kwargs = {'header': header, 'encoding': encoding}

    archive = tmp_path / 'spam.zip'
    filename = 'spam.csv'
    with zipfile.ZipFile(archive, 'w') as z,\
         z.open(filename, 'w') as f:
        if encoding is None:
            with pytest.raises(expected[0], match=expected[1]):
                write_csv(f, rows, **kwargs)
            return

        result = write_csv(f, rows, **kwargs)

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
@pytest.mark.parametrize(
    'filename, rows, header, encoding, expected',
    [('spam.csv', ROWS, None, ENCODING, BYTES),
     ('spam.csv', ROWS, HEADER, ENCODING, H_BYTES + BYTES),
     (pathlib.Path('spam.csv'), ROWS, None, ENCODING, BYTES),
     ('nonfilename', ROWS, None, None, (TypeError, r'need encoding'))])
def test_write_csv_filename(tmp_path, filename, rows, header, encoding, expected):
    if sys.version_info < (3, 6):
        tmp_path = pathlib.Path(str(tmp_path))

    kwargs = {'header': header, 'encoding': encoding}

    if isinstance(expected, tuple):
        assert encoding is None
        with pytest.raises(expected[0], match=expected[1]):
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
@pytest.mark.parametrize(
    'rows, header, encoding, hash_name, expected',
    [(ROWS, None, ENCODING, 'sha256', 'c793b37cb2008e5591d127db8232085e'
                                      '64944cae5315ca886f57988343f5b111'),
     (ROWS, HEADER, ENCODING, 'sha256', 'ddbbcd4f1b15f3834f5a9ee59a6ee7837'
                                        '7474df6d9b017216b89129ecc394608'),
     (ROWS, None, ENCODING, 'md5', '67bac4eb7cd16ea8eaf454eafa559d34'),
     (ROWS, None, 'utf-16', 'sha1', {'little': 'b0e0578b8149619569a4f56a3e6d05fed7de788f',
                                     'big': 'cdb41df63c3c5e87ce4c87cfa6058b2e81c40112'}[sys.byteorder]),
     (ROWS, None, 'utf-16-le', 'sha1', '3f49d7d103251f7d4db79ca6eac67f239c71327a'),
     (ROWS, None, 'utf-16-be', 'sha1', '69e6b3af0972e350bbc7f6dd9bb92f13d2e9fee0'),
     (ROWS, None, None, 'sha256', (TypeError, r'need encoding'))])
def test_write_csv_hash(rows, header, encoding, hash_name, expected):
    kwargs = {'header': header, 'encoding': encoding}
    hashsum = hashlib.new(hash_name)

    if isinstance(expected, tuple):
        assert encoding is None
        with pytest.raises(expected[0], match=expected[1]):
            write_csv(hashsum, rows, **kwargs)
        return

    result = write_csv(hashsum, rows, **kwargs)

    assert result is hashsum
    assert result.hexdigest() == expected


@pytest.csv23.py3only
@pytest.mark.parametrize(
    'rows, header, encoding, hash_name',
    [(ROWS, HEADER, ENCODING, 'sha256'),
     (ROWS, HEADER, 'utf-16', 'sha1')])
def test_write_csv_equivalence(tmp_path, rows, header, encoding, hash_name):
    if sys.version_info < (3, 6):
        tmp_path = pathlib.Path(str(tmp_path))

    make_hash = functools.partial(hashlib.new, hash_name)

    kwargs = {'header': header, 'encoding': encoding}

    r_hash = write_csv(make_hash(), rows, **kwargs)

    r_none = write_csv(None, rows, **kwargs)
    r_write = write_csv(io.BytesIO(), rows, **kwargs).getvalue()
    r_filename = write_csv(tmp_path / 'spam.csv', rows, **kwargs).read_bytes()

    assert (r_hash.hexdigest()
            == make_hash(r_none).hexdigest()
            == make_hash(r_write).hexdigest()
            == make_hash(r_filename).hexdigest())


@pytest.csv23.py3only
@pytest.mark.parametrize(
    'filename, open_module, raw, encoding, rows',
    [('spam.csv.bz2', 'bz2', BYTES, ENCODING, ROWS),
     ('spam.csv.gz', 'gzip', BYTES, ENCODING, ROWS),
     ('spam.csv.xz', 'lzma', BYTES, ENCODING, ROWS)])
@pytest.csv23.py3only
def test_roundtrip_csv_autocompress(tmp_path, filename, open_module,
                                    raw, encoding, rows):
    if sys.version_info < (3, 6):
        tmp_path = pathlib.Path(str(tmp_path))

    target = tmp_path / filename

    filename = str(target) if sys.version_info < (3, 6) else target

    import importlib

    open_module = importlib.import_module(open_module)

    with open_module.open(filename, 'wb') as f:
        f.write(raw)

    kwargs = {'encoding': encoding, 'autocompress': True}

    assert read_csv(filename, as_list=True, **kwargs) == rows

    target.unlink()

    result = write_csv(filename, rows, **kwargs)

    assert result.exists()
    assert result.samefile(target)

    assert read_csv(filename, as_list=True, **kwargs) == rows


@pytest.csv23.py3only
def test_autocompress_warning(tmp_path):
    if sys.version_info < (3, 6):
        tmp_path = pathlib.Path(str(tmp_path))

    target = tmp_path / 'spam.csv.gz'
    target.touch()

    filename = str(target) if sys.version_info < (3, 6) else target

    with pytest.warns(UserWarning, match=r'suffix'):
        read_csv(filename)
