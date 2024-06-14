from vancelle.lib.heavymetal import HeavymetalTuple


def bi(name: str) -> HeavymetalTuple:
    """
    >>> from vancelle.lib.heavymetal import render
    >>> render(bi("bootstrap"))
    '<i class="bi bi-bootstrap"></i>'
    """
    return ("i", {"class": f"bi bi-{name}"}, [])
