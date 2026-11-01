from csv23._workarounds import issue12178, issue31590


def test_issue12178():
    assert not issue12178()


def test_issue31590():
    assert not issue31590()
