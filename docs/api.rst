.. _api:

API Reference
=============

High level interface
--------------------

.. autosummary::
    :nosignatures:

    csv23.open_csv
    csv23.open_reader
    csv23.open_writer
    csv23.iterrows
    csv23.read_csv
    csv23.write_csv


CSV readers and writers
-----------------------

.. autosummary::
    :nosignatures:

    csv23.reader
    csv23.writer
    csv23.DictReader
    csv23.DictWriter
    csv23.NamedTupleReader
    csv23.NamedTupleWriter


open_csv
--------

.. autofunction:: csv23.open_csv


open_reader/writer
------------------

.. autofunction:: csv23.open_reader
.. autofunction:: csv23.open_writer


iterrows
--------

.. autofunction:: csv23.iterrows


read_csv/write_csv
------------------

.. autofunction:: csv23.read_csv
.. autofunction:: csv23.write_csv


reader/writer
-------------

.. autofunction:: csv23.reader
.. autofunction:: csv23.writer


DictReader/Writer
-----------------

.. autoclass:: csv23.DictReader
.. autoclass:: csv23.DictWriter


NamedTupleReader/Writer
-----------------------

.. autoclass:: csv23.NamedTupleReader
    :members:
        __next__,
        dialect, line_num,
        row_cls

.. autoclass:: csv23.NamedTupleWriter
    :members:
        writerow, writerows,
        dialect
