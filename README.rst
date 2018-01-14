csv23
=====

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


License
-------

This package is distributed under the `MIT license`_.


.. _pip: https://pip.readthedocs.io

.. _MIT license: https://opensource.org/licenses/MIT


.. |--| unicode:: U+2013
