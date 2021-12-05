"""Verify stdlib csv behaviour for workarounds."""

import csv
import io
import sys

import pytest

FORMATS = [
    ('quoting', 'quotechar', 'escapechar', 'doublequote'),
    (csv.QUOTE_MINIMAL, '"', None, True),    # quotes: ,\r\n" doubles: "
    (csv.QUOTE_MINIMAL, '"', None, False),   # quotes: ,\r\n need to escape: "
    (csv.QUOTE_MINIMAL, '"', '\\', True),    # quotes: ,\r\n"\\ doubles: " issue12178
    (csv.QUOTE_MINIMAL, '"', '\\', False),   # quotes: ,\r\n\\ escapes: " issue12178
    (csv.QUOTE_MINIMAL, None, None, True),   # quotechar must be set if quoting enabled
    (csv.QUOTE_MINIMAL, None, None, False),  # quotechar must be set if quoting enabled
    (csv.QUOTE_MINIMAL, None, '\\', True),   # quotechar must be set if quoting enabled
    (csv.QUOTE_MINIMAL, None, '\\', False),  # quotechar must be set if quoting enabled
    (csv.QUOTE_NONE, '"', None, True),       # need to escape: ,\r\n"
    (csv.QUOTE_NONE, '"', None, False),      # need to escape: ,\r\n"
    (csv.QUOTE_NONE, '"', '\\', True),       # escapes: ,\r\n"\\ issue31590
    (csv.QUOTE_NONE, '"', '\\', False),      # escapes: ,\r\n"\\ issue31590
    (csv.QUOTE_NONE, None, None, True),      # need to escape: ,\r\n
    (csv.QUOTE_NONE, None, None, False),     # need to escape: ,\r\n
    (csv.QUOTE_NONE, None, '\\', True),      # escapes: ,\r\n\\ issue31590
    (csv.QUOTE_NONE, None, '\\', False),     # escapes: ,\r\n\\ issue31590
]

VALUES = ['spam, eggs',
          'spam\r eggs',
          'spam\n eggs',
          'spam "spam" eggs',
          '"spam spam eggs"',
          'spam\\eggs']


@pytest.mark.parametrize(', '.join(FORMATS[0]), FORMATS[1:])
@pytest.mark.parametrize('value', VALUES)
def test_csv_roundtrip(py2, quoting, quotechar, escapechar, doublequote, value):
    csv_kwargs = {'quoting': quoting, 'quotechar': quotechar,
                  'escapechar': escapechar, 'doublequote': doublequote}
    row = expected = [value]

    with io.BytesIO() if py2 else io.StringIO(newline='') as f:
        if quoting != csv.QUOTE_NONE and quotechar is None:
            with pytest.raises(TypeError, match=r'quotechar must be set'):
                csv.writer(f, **csv_kwargs)
            return

        writer = csv.writer(f, **csv_kwargs)

        if escapechar is None and (quoting == csv.QUOTE_NONE or not doublequote):
            need_escape = [',', '\r', '\n'] if quoting == csv.QUOTE_NONE else []
            if quotechar is not None:
                need_escape.append(quotechar)
            if any(n in value for n in need_escape):
                with pytest.raises(Exception, match=r'need to escape'):
                    writer.writerow(row)
                return

        writer.writerow(row)
        f.seek(0)
        row = next(csv.reader(f, **csv_kwargs))

    if quoting != csv.QUOTE_NONE and escapechar is not None and escapechar in value:
        # writer fails to escape escapechar
        if sys.version_info < (3, 10):
            assert row != expected
            pytest.xfail(reason='https://bugs.python.org/issue12178')
        else:
            assert row == expected
    elif py2 and quoting == csv.QUOTE_NONE and escapechar is not None and '\n' in value:
        # reader fails to recognize escaped newline
        assert row != expected
        pytest.xfail(reason='https://bugs.python.org/issue31590')
        # see also https://bugs.python.org/issue15927
    else:
        assert row == expected
