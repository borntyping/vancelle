from vancelle.html.document import div, h1, header, p, section
from vancelle.html.helpers import html_classes
from vancelle.html.hotmetal import Hotmetal, element


def _header(
    title: str,
    subtitle: str | None,
    fields: Hotmetal | None,
    title_class: str,
    subtitle_class: str,
) -> Hotmetal:
    text = div(
        {},
        [
            h1({"class": html_classes("title", title_class)}, [title]),
            p({"class": html_classes("subtitle", subtitle_class)}, [subtitle]),
        ],
    )

    columns = [div({"class": "column"}, [text])]
    if fields:
        columns.append(div({"class": "column"}, [div({"class": "field is-grouped is-grouped-right"}, [fields])]))

    return header({"class": "block"}, [div({"class": "columns"}, columns)])


def heading(title: str, subtitle: str | None = None, fields: Hotmetal | None = None) -> Hotmetal:
    return _header(title=title, subtitle=subtitle, fields=fields, title_class="is-3", subtitle_class="is-5")


def subheading(title: str, subtitle: str | None = None, fields: Hotmetal | None = None) -> Hotmetal:
    return _header(title=title, subtitle=subtitle, fields=fields, title_class="is-3", subtitle_class="is-5")


def block_section(*children: Hotmetal) -> Hotmetal:
    return section({"class": "block"}, children)
