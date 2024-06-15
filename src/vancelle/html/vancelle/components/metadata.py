import datetime

import humanize
import markupsafe

from vancelle.extensions import html
from vancelle.html.bootstrap_icons import bi_font
from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import a, span


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
            "class": "icon-link",
            "rel": "noopener noreferrer nofollow",
            "target": "_blank",
            "title": href,
        },
        [
            bi_font("box-arrow-up-right"),
            url(href, text),
        ],
    )


def span_date(d: datetime.date | None) -> Heavymetal:
    if not isinstance(d, datetime.date):
        raise ValueError(f"Not a date: {d!r}")

    formatted = humanize.naturaldate(d)
    joined = markupsafe.Markup(formatted.replace(" ", "&nbsp;"))
    return span({"class": "x-has-tabular-nums", "title": str(d)}, [joined])
