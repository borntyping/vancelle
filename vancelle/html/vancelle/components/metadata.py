from vancelle.extensions import html
from vancelle.html.bulma.elements.icon import icon
from vancelle.html.document import a, span
from vancelle.html.hotmetal import Hotmetal


def absent() -> Hotmetal:
    return span({"class": "x-absent"}, html.ABSENT)


def url(href: str, text: str | None) -> Hotmetal:
    return span({}, [text or html.pretty_url(href)])


def internal_url(href: str, text: str | None = None) -> Hotmetal:
    return a(
        {
            "href": href,
            "class": "has-text-link is-flex-wrap-nowrap",
        },
        [url(href, text)],
    )


def external_url(href: str, text: str | None = None) -> Hotmetal:
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
