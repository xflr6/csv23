import csv

__all__ = ['unix_dialect', 'AsciiDelimited']


def register(name):
    def decorate(cls):
        csv.register_dialect(name, cls)
        return cls
    return decorate


unix_dialect = csv.unix_dialect


@register(str('ascii'))
class AsciiDelimited(csv.Dialect):
    """https://en.wikipedia.org/wiki/Delimiter#ASCII_Delimited_Text"""

    delimiter = str('\x1f')  # https://en.wikipedia.org/wiki/Unit_separator
    quotechar = escapechar = None
    doublequote = False
    skipinitialspace = False
    lineterminator = str('\x1e')  # https://en.wikipedia.org/wiki/Record_separator
    quoting = csv.QUOTE_NONE
    strict = True
