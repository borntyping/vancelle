from .grid import row, col


def test_row():
    assert row({"class": "example"}, []) == ("div", {"class": "row example"}, [])


def test_col():
    assert col({"class": "example"}, []) == ("div", {"class": "col example"}, [])
