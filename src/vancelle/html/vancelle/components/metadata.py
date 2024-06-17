import datetime

import humanize
import markupsafe
import urllib.parse

from vancelle.html.bootstrap_icons import bi_svg
from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import a, span


def internal_url(href: str, text: str) -> Heavymetal:
    return a({"href": href, "class": "has-text-link is-flex-wrap-nowrap"}, [text])


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
            span({}, [text or urllib.parse.urlparse(href).hostname]),
            bi_svg("box-arrow-up-right"),
        ],
    )


def span_date(d: datetime.date | None) -> Heavymetal:
    if not isinstance(d, datetime.date):
        raise ValueError(f"Not a date: {d!r}")

    formatted = humanize.naturaldate(d)
    joined = markupsafe.Markup(formatted.replace(" ", "&nbsp;"))
    return span({"class": "x-has-tabular-nums", "title": str(d)}, [joined])
