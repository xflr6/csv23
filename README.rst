csv23
=====

|PyPI version| |License| |Supported Python| |Format| |Docs|

|Travis| |Codecov|

``csv23`` provides the unicode-based API of the Python 3 ``csv`` module for
Python 2 and 3. Code that should run under both versions of Python can use it
to hide the ``bytes`` vs. ``text`` difference between 2 and 3 and stick to the
newer unicode-based interface.

The package also provides simple convenience functionality such as the
``open_csv()`` context manager for opening a CSV file in the right mode and
returning a ``csv.reader`` or ``csv.writer``:

.. code:: python

    >>> import csv23

    >>> with csv23.open_csv('spam.csv') as reader:  # doctest: +SKIP
    ...     for row in reader:
    ...         print(', '.join(row))
    Spam!, Spam!, Spam!'
    Spam!, Lovely Spam!, Lovely Spam!'

It uses ``utf-8`` as default encoding everywhere.


Links
-----

- GitHub: https://github.com/xflr6/csv23
- PyPI: https://pypi.python.org/pypi/csv23
- Documentation: https://csv23.readthedocs.io
- Changelog: https://csv23.readthedocs.io/en/latest/changelog.html
- Issue Tracker: https://github.com/xflr6/csv23/issues
- Download: https://pypi.python.org/pypi/csv23#downloads


Installation
------------

This package runs under Python 2.7, and 3.4+, use pip_ to install:

.. code:: bash

    $ pip install csv23


See also
--------

- https://docs.python.org/2/library/csv.html#examples (UnicodeReader, UnicodeWriter)
- https://agate.readthedocs.io/en/latest/api/csv.html
- https://pypi.python.org/pypi/backports.csv
- https://pypi.python.org/pypi/csv342


License
-------

This package is distributed under the `MIT license`_.


.. _pip: https://pip.readthedocs.io

.. _MIT license: https://opensource.org/licenses/MIT


.. |--| unicode:: U+2013


.. |PyPI version| image:: https://img.shields.io/pypi/v/csv23.svg
    :target: https://pypi.python.org/pypi/csv23
    :alt: Latest PyPI Version
.. |License| image:: https://img.shields.io/pypi/l/csv23.svg
    :target: https://pypi.python.org/pypi/csv23
    :alt: License
.. |Supported Python| image:: https://img.shields.io/pypi/pyversions/csv23.svg
    :target: https://pypi.python.org/pypi/csv23
    :alt: Supported Python Versions
.. |Format| image:: https://img.shields.io/pypi/format/csv23.svg
    :target: https://pypi.python.org/pypi/csv23
    :alt: Format
.. |Downloads| image:: https://img.shields.io/pypi/dm/csv23.svg
    :target: https://pypi.python.org/pypi/csv23
    :alt: Downloads
.. |Docs| image:: https://readthedocs.org/projects/csv23/badge/?version=stable
    :target: https://csv23.readthedocs.io/en/stable/
    :alt: Readthedocs
.. |Travis| image:: https://img.shields.io/travis/xflr6/csv23.svg
    :target: https://travis-ci.org/xflr6/csv23
    :alt: Travis
.. |Codecov| image:: https://codecov.io/gh/xflr6/csv23/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/xflr6/csv23
    :alt: Codecov
