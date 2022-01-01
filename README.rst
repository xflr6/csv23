csv23
=====

|PyPI version| |License| |Supported Python| |Wheel|

|Build| |Codecov| |Readthedocs-stable| |Readthedocs-latest|

``csv23`` provides the unicode-based API of the Python 3 ``csv`` module for
Python 2 and 3. Code that should run under both versions of Python can use it
to hide the ``bytes`` vs. ``text`` difference between 2 and 3 and stick to the
newer unicode-based interface.

It uses ``utf-8`` as default encoding everywhere.


Improvements
------------

``csv23`` works around for the following bugs in the stdlib ``csv`` module:

bpo-12178_
  broken round-trip with ``escapechar`` if your data contains a literal escape
  character (fixed in Python 3.10)

bpo-31590_
  broken round-trip with ``escapechar`` and embedded newlines under Python 2
  (fixed in Python 3.4 but not backported): produce a warning


Links
-----

- GitHub: https://github.com/xflr6/csv23
- PyPI: https://pypi.org/project/csv23/
- Documentation: https://csv23.readthedocs.io
- Changelog: https://csv23.readthedocs.io/en/latest/changelog.html
- Issue Tracker: https://github.com/xflr6/csv23/issues
- Download: https://pypi.org/project/csv23/#files


Extras
------

The package also provides some convenience functionality such as the
``open_csv()`` context manager for opening a CSV file in the right mode and
returning a ``csv.reader`` or ``csv.writer``:

.. code:: python

    >>> import csv23

    >>> with csv23.open_csv('spam.csv') as reader:  # doctest: +SKIP
    ...     for row in reader:
    ...         print(', '.join(row))
    Spam!, Spam!, Spam!'
    Spam!, Lovely Spam!, Lovely Spam!'


Python 3 Extras
---------------

The ``read_csv()`` and ``write_csv()`` functions (available on Python 3 only)
are most useful if you want (or need to) open a file-like object in the calling
code, e.g. when reading or writing directly to a binary stream such as a ZIP
file controlled by the caller (emulated with a ``io.BytesIO`` below):

.. code:: python

    >>> import io
    >>> buf = io.BytesIO()

    >>> import zipfile
    >>> with zipfile.ZipFile(buf, 'w') as z, z.open('spam.csv', 'w') as f:
    ...     csv23.write_csv(f, [[1, None]], header=['spam', 'eggs'])
    <zipfile...>

    >>> buf.seek(0)
    0

    >>> with zipfile.ZipFile(buf) as z, z.open('spam.csv') as f:
    ...     csv23.read_csv(f, as_list=True)
    [['spam', 'eggs'], ['1', '']]

``csv23`` internally wraps the byte stream in a ``io.TextIOWrapper`` with the
given encoding and ``newline=''`` (see ``csv`` module docs_).

The ``write_csv()``-function also supports updating objects with a
``.update(<bytes>)``-method such as ``hashlib.new()`` instances, which allows
to calculate a checksum over the binary CSV file output produced from the given
rows without writing it to disk (note that the object is returned):

.. code:: python

    >>> import hashlib

    >>> csv23.write_csv(hashlib.new('sha256'), [[1, None]], header=['spam', 'eggs']).hexdigest()
    'aed6871f9ca7c047eb55a569e8337af03fee508521b5ddfe7ad0ad1e1139980a'

Both functions have an optional ``autocompress`` argument: Set it to ``True``
to transparently compress (or decompress) if the file argument is a path that
ends in one of ``'.bz2'``, ``'.gz'``, and ``'.xz'``.


Installation
------------

This package runs under Python 2.7, and 3.7+, use pip_ to install:

.. code:: bash

    $ pip install csv23


See also
--------

- https://docs.python.org/2/library/csv.html#examples (UnicodeReader, UnicodeWriter)
- https://agate.readthedocs.io/en/latest/api/csv.html
- https://pypi.org/project/backports.csv/
- https://pypi.org/project/csv342/


License
-------

This package is distributed under the `MIT license`_.


.. _bpo-12178: https://bugs.python.org/issue12178
.. _bpo-31590: https://bugs.python.org/issue31590

.. _pip: https://pip.readthedocs.io

.. _docs: https://docs.python.org/3/library/csv.html#csv.reader

.. _MIT license: https://opensource.org/licenses/MIT


.. |--| unicode:: U+2013


.. |PyPI version| image:: https://img.shields.io/pypi/v/csv23.svg
    :target: https://pypi.org/project/csv23/
    :alt: Latest PyPI Version
.. |License| image:: https://img.shields.io/pypi/l/csv23.svg
    :target:  https://github.com/xflr6/csv23/blob/master/LICENSE.txt
    :alt: License
.. |Supported Python| image:: https://img.shields.io/pypi/pyversions/csv23.svg
    :target: https://pypi.org/project/csv23/
    :alt: Supported Python Versions
.. |Wheel| image:: https://img.shields.io/pypi/wheel/csv23.svg
    :target: https://pypi.org/project/csv23/#files

.. |Build| image:: https://github.com/xflr6/csv23/actions/workflows/build.yaml/badge.svg?branch=master
    :target: https://github.com/xflr6/csv23/actions/workflows/build.yaml?query=branch%3Amaster
    :alt: Build
.. |Codecov| image:: https://codecov.io/gh/xflr6/csv23/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/xflr6/csv23
    :alt: Codecov
.. |Readthedocs-stable| image:: https://readthedocs.org/projects/csv23/badge/?version=stable
    :target: https://csv23.readthedocs.io/en/stable/?badge=stable
    :alt: Readthedocs stable
.. |Readthedocs-latest| image:: https://readthedocs.org/projects/csv23/badge/?version=latest
    :target: https://csv23.readthedocs.io/en/latest/?badge=latest
    :alt: Readthedocs latest