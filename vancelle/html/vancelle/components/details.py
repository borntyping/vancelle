import textwrap

from vancelle.html.vancelle.components.optional import ABSENT, maybe_string
from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import a, fragment, span
from vancelle.models.details import Details


def details_title(details: Details, *, href: str | None) -> Heavymetal:
    title = maybe_string(details.title)
    return a({"href": href}, [title]) if href else span({}, [title])


def details_date_and_author(details: Details) -> Heavymetal:
    year = str(details.release_date.year) if details.release_date else ABSENT
    author = textwrap.shorten(details.author, 50) if details.author else ABSENT

    return fragment(
        [
            span({"title": maybe_string(details.release_date)}, [year]),
            ", ",
            span({"title": maybe_string(details.author)}, [author]),
        ]
    )
