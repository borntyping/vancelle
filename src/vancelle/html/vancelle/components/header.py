import typing

from vancelle.html.helpers import HtmlClasses, html_classes
from vancelle.lib.heavymetal import Heavymetal, HeavymetalContent
from vancelle.lib.heavymetal.html import div, element, header, nothing


def _header(
    *,
    tag: typing.Literal["h1", "h2", "h3"],
    title: str,
    subtitle: str | None,
    controls: HeavymetalContent,
    header_classes: HtmlClasses = (),
    title_classes: HtmlClasses = (),
    subtitle_classes: HtmlClasses = (),
) -> Heavymetal:
    return header(
        {"class": html_classes("d-flex justify-content-between align-items-center", header_classes)},
        [
            div(
                {},
                [
                    element(tag, {"class": html_classes(title_classes)}, [title]),
                    element("p", {"class": html_classes("lead", subtitle_classes)}, [subtitle]) if subtitle else nothing(),
                ],
            ),
            div({}, [*controls]),
        ],
    )


def page_header(title: str, subtitle: str | None = None, controls: HeavymetalContent = ()) -> Heavymetal:
    return _header(
        tag="h1",
        title=title,
        subtitle=subtitle,
        controls=controls,
        header_classes="mb-5",
        title_classes="display-3",
        subtitle_classes="fs-4",
    )


def section_header(title: str, subtitle: str | None = None, controls: HeavymetalContent = ()) -> Heavymetal:
    return _header(
        tag="h2",
        title=title,
        subtitle=subtitle,
        controls=controls,
        header_classes="mt-5 mb-2",
        title_classes="m-0",
        subtitle_classes="",
    )
