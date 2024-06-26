import datetime
import typing

from vancelle.lib.heavymetal import Heavymetal, HeavymetalContent
from vancelle.lib.heavymetal.html import fragment, span

ABSENT = "—"


def span_absent() -> Heavymetal:
    return span({"class": "x-absent"}, [ABSENT])


def maybe_str(value: typing.Any | None) -> str:
    return str(value) if value else ABSENT


def maybe_year(value: datetime.date | None) -> str:
    return str(value.year) if value is not None else ABSENT


def maybe_span(string: str | None) -> Heavymetal:
    return span({}, [string]) if string is not None else span_absent()


def quote_str(value: str | None) -> str:
    return f"“{value}”" if value is not None else ABSENT


def quote(content: HeavymetalContent) -> Heavymetal:
    return fragment(["“", *content, "”"])
