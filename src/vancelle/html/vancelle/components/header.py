import typing

from vancelle.lib.html import HtmlClasses, html_classes
from vancelle.lib.heavymetal import Heavymetal, HeavymetalAnything, HeavymetalContent
from vancelle.lib.heavymetal.html import div, element, header, nothing


def _header(
    *,
    tag: typing.Literal["h1", "h2", "h3"],
    title: Heavymetal,
    subtitle: Heavymetal | None,
    controls: HeavymetalContent,
    header_classes: HtmlClasses = (),
    title_classes: HtmlClasses = (),
    subtitle_classes: HtmlClasses = (),
) -> Heavymetal:
    return header(
        {"class": header_classes},
        [
            div(
                {"class": "d-flex justify-content-between align-items-center"},
                [
                    element(tag, {"class": html_classes("mb-0", title_classes)}, [title]),
                    div({}, [*controls]),
                ],
            ),
            div({}, [element("p", {"class": html_classes("lead", subtitle_classes)}, [subtitle]) if subtitle else nothing()]),
        ],
    )


def PageHeader(title: Heavymetal, subtitle: Heavymetal | None = None, *controls: HeavymetalAnything) -> Heavymetal:
    return _header(
        tag="h1",
        title=title,
        subtitle=subtitle,
        controls=controls,
        header_classes="v-block",
        title_classes="display-3",
        subtitle_classes="fs-4 ps-1",
    )


def SectionHeader(title: Heavymetal, subtitle: Heavymetal | None = None, *controls: HeavymetalAnything) -> Heavymetal:
    return _header(
        tag="h2",
        title=title,
        subtitle=subtitle,
        controls=controls,
        header_classes="mb-2",
        title_classes="m-0",
        subtitle_classes="",
    )
