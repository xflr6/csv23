Changelog
=========


Version 0.3.5 (in development)
------------------------------

Tag Python 3.11 support.


Version 0.3.4
-------------

Drop Python 3.6 support.


Version 0.3.3
-------------

Drop Python 3.5 support and tag Python 3.9 and 3.10 support.


Version 0.3.2
-------------

Fix failing ``test_write_csv_hash()`` on big-endian platforms.


Version 0.3.1
-------------

Add workaround for PyPy to ``write_csv()`` when used with a ``hashlib`` hash.


Version 0.3
-----------

Add ``autocompress`` option to ``read_csv()`` and ``write_csv()``
(Python 3 only): automatically (de)compresses if  file is a path and ends with
``'.bz2'``, ``'.gz'``, or ``'.xz'``.


Version 0.2
-----------

Add ``read_csv()`` and ``write_csv()`` functions for working with open
(e.g. binary) streams (file-like objects). Available under Python 3 only.


Version 0.1.6
-------------

Tag Python 3.8 support.


Version 0.1.5
-------------

Add ``row_name`` argument to ``NamedTupleReader``.

Drop Python 3.4 support, tag Python 3.7 support.

Extend documentation and improve formatting.


Version 0.1.4
-------------

Document workarounds for https://bugs.python.org/issue12178 and
https://bugs.python.org/issue31590 bugs.

Add ``rowtype='namedtuple'`` for ``collections.namedtuple`` reader and writer.


Version 0.1.3
-------------

Fix missing ``mock`` install requirement in ``setup.py``.


Version 0.1.2
-------------

Convert unicode values for format parameters like ``delimiter`` to bytes on PY2.

Add PY2 backport of ``csv.unix_dialect``.

Add ``QUOTE_*`` constants, ``Error``, dialects, and associated functions from ``csv`` to csv23 namespace.


Version 0.1.1
-------------

Fix ``issue31590()`` check.

Add documentation and CI links to ``README.txt``.


Version 0.1
-----------

Initial release (provisional API).
