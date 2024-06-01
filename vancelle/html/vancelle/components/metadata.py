import datetime

import humanize
import markupsafe

from vancelle.extensions import html
from vancelle.html.bulma.elements.icon import icon
from vancelle.lib.heavymetal.html import a, span
from vancelle.lib.heavymetal import Heavymetal


def url(href: str, text: str | None) -> Heavymetal:
    return span({}, [text or html.pretty_url(href)])


def internal_url(href: str, text: str | None = None) -> Heavymetal:
    return a(
        {
            "href": href,
            "class": "has-text-link is-flex-wrap-nowrap",
        },
        [url(href, text)],
    )


def external_url(href: str, text: str | None = None) -> Heavymetal:
    return a(
        {
            "href": href,
            "class": "has-text-link is-flex-wrap-nowrap icon-text",
            "rel": "noopener noreferrer nofollow",
            "target": "_blank",
            "title": href,
        },
        [icon("exit-outline"), url(href, text)],
    )


def span_date(d: datetime.date | None) -> Heavymetal:
    if not isinstance(d, datetime.date):
        raise ValueError(f"Not a date: {d!r}")

    formatted = humanize.naturaldate(d)
    joined = markupsafe.Markup(formatted.replace(" ", "&nbsp;"))
    return span({"class": "x-has-tabular-nums", "title": str(d)}, [joined])
