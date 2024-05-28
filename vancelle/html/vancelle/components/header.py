import typing

from vancelle.html.document import div, header, p, section
from vancelle.html.helpers import html_classes
from vancelle.html.hotmetal import Hotmetal, element


def _complex_header(
    tag: typing.Literal["h1", "h2"],
    title: str,
    subtitle: str | None,
    fields: Hotmetal | None,
    title_class: str,
    subtitle_class: str,
) -> Hotmetal:
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
) -> Hotmetal:
    return header(
        {"class": "block"},
        [
            element(tag, {"class": html_classes("title", title_class)}, [title]),
            element("p", {"class": html_classes("subtitle", subtitle_class)}, [subtitle]),
        ],
    )


def page_header(title: str, subtitle: str | None = None) -> Hotmetal:
    return _header(tag="h1", title=title, subtitle=subtitle, title_class="is-2", subtitle_class="is-4")


def section_header(title: str, subtitle: str | None = None) -> Hotmetal:
    return _header(tag="h2", title=title, subtitle=subtitle, title_class="is-3", subtitle_class="is-5")


def card_header(title: str, subtitle: str | None = None) -> Hotmetal:
    return _header(tag="h3", title=title, subtitle=subtitle, title_class="is-4", subtitle_class="is-6")


def block_section(*children: Hotmetal) -> Hotmetal:
    return element("section", {"class": "block"}, children)
