import typing

from vancelle.lib.heavymetal.html import div, element, header, p
from vancelle.html.helpers import html_classes
from vancelle.lib.heavymetal import Heavymetal


def _complex_header(
    tag: typing.Literal["h1", "h2"],
    title: str,
    subtitle: str | None,
    fields: Heavymetal | None,
    title_class: str,
    subtitle_class: str,
) -> Heavymetal:
    text = div(
        {},
        [
            element(tag, {"class": html_classes("title", title_class)}, [title]),
            p({"class": html_classes("subtitle", subtitle_class)}, [subtitle]),
        ],
    )

    columns = [div({"class": "column"}, [text])]
    if fields:
        columns.append(div({"class": "column"}, [div({"class": "field is-grouped is-grouped-right"}, [fields])]))

    return header({"class": "block"}, [div({"class": "columns"}, columns)])


def _header(
    tag: typing.Literal["h1", "h2", "h3"],
    title: str,
    subtitle: str | None,
    title_class: str,
    subtitle_class: str,
) -> Heavymetal:
    return header(
        {"class": "block"},
        [
            element(tag, {"class": html_classes("title", title_class)}, [title]),
            element("p", {"class": html_classes("subtitle", subtitle_class)}, [subtitle]),
        ],
    )


def page_header(title: str, subtitle: str | None = None) -> Heavymetal:
    return _header(tag="h1", title=title, subtitle=subtitle, title_class="is-2", subtitle_class="is-4")


def section_header(title: str, subtitle: str | None = None) -> Heavymetal:
    return _header(tag="h2", title=title, subtitle=subtitle, title_class="is-3", subtitle_class="is-5")


def card_header(title: str, subtitle: str | None = None) -> Heavymetal:
    return _header(tag="h3", title=title, subtitle=subtitle, title_class="is-4", subtitle_class="is-6")


def block_section(*children: Heavymetal) -> Heavymetal:
    return element("section", {"class": "block"}, children)
