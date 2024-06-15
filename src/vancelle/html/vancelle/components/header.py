import typing

from vancelle.html.helpers import HtmlClasses, html_classes
from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import element, header, nothing


def _header(
    tag: typing.Literal["h1", "h2", "h3"],
    title: str,
    subtitle: str | None,
    *,
    header_classes: HtmlClasses = (),
    title_classes: HtmlClasses = (),
    subtitle_classes: HtmlClasses = (),
) -> Heavymetal:
    return header(
        {"class": html_classes(header_classes)},
        [
            element(tag, {"class": html_classes(title_classes)}, [title]),
            element("p", {"class": html_classes("lead", subtitle_classes)}, [subtitle]) if subtitle else nothing(),
        ],
    )


def page_header(title: str, subtitle: str | None = None) -> Heavymetal:
    return _header("h1", title, subtitle, header_classes="", title_classes="display-3", subtitle_classes="fs-3")


def section_header(title: str, subtitle: str | None = None) -> Heavymetal:
    return _header("h2", title, subtitle, header_classes="mt-5 mb-2", title_classes="m-0 display-6", subtitle_classes="fs-5")
