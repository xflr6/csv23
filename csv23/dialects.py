"""Backport unix_dialect."""

from __future__ import unicode_literals

import csv

from ._common import PY2

__all__ = ['unix_dialect', 'AsciiDelimited']


def register(name):
    def decorate(cls):
        csv.register_dialect(name, cls)
        return cls
    return decorate


if PY2:
    @register(b'unix')
    class unix_dialect(csv.Dialect):  # noqa: N801
        """Describe the usual properties of Unix-generated CSV files."""

        delimiter = b','
        quotechar = b'"'
        doublequote = True
        skipinitialspace = False
        lineterminator = b'\n'
        quoting = csv.QUOTE_ALL


else:
    unix_dialect = csv.unix_dialect


@register(str('ascii'))
class AsciiDelimited(csv.Dialect):
    """https://en.wikipedia.org/wiki/Delimiter#ASCII_Delimited_Text"""

    delimiter = str('\x1f')  # https://en.wikipedia.org/wiki/Unit_separator
    quotechar = escapechar =  None
    doublequote = False
    skipinitialspace = False
    lineterminator = str('\x1e')  # https://en.wikipedia.org/wiki/Record_separator
    quoting = csv.QUOTE_NONE
    strict = True
