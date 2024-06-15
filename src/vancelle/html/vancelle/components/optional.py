import typing

from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import span

ABSENT = "—"


def span_absent() -> Heavymetal:
    return span({"class": "x-absent"}, [ABSENT])


def maybe_string(value: typing.Any | None) -> str:
    return str(value) if value else ABSENT


def maybe_span(string: str | None) -> Heavymetal:
    return span({}, [string]) if string is not None else span_absent()
