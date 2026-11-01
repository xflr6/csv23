import csv
import io

ESCAPECHAR = '\\'


def issue12178(escapechar=ESCAPECHAR):
    with io.StringIO(newline='') as stream:
        csv.writer(stream, escapechar=escapechar).writerow([escapechar])
        line = stream.getvalue()
    return (escapechar * 2) not in line


def issue31590(line='spam%s\neggs,spam\r\n' % ESCAPECHAR, escapechar=ESCAPECHAR):
    with io.StringIO(line, newline='') as stream:
        reader = csv.reader(stream, quoting=csv.QUOTE_NONE, escapechar=escapechar)
        row = next(reader)
    return len(row) != 2
