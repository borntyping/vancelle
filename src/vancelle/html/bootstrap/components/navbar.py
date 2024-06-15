"""
https://getbootstrap.com/docs/5.3/components/navbar/
"""

import typing

from vancelle.html.helpers import html_classes
from vancelle.lib.heavymetal import Heavymetal, HeavymetalDynamicContent
from vancelle.lib.heavymetal.html import a, button, div, fragment, nav, span, ul

DropdownItem = typing.NewType("DropdownItem", Heavymetal)
DropdownDivider = typing.NewType("DropdownDivider", Heavymetal)


def navbar(brand: Heavymetal, left: HeavymetalDynamicContent, right: HeavymetalDynamicContent) -> Heavymetal:
    return nav(
        {"class": "navbar navbar-expand-lg bg-primary", "data-bs-theme": "dark"},
        [
            div(
                {"class": "container"},
                [
                    brand,
                    navbar_toggler([
                        navbar_nav_left(left),
                        navbar_nav_right(right),
                    ]),
                ],
            )
        ],
    )


def navbar_brand(name: str, href: str) -> Heavymetal:
    return a({"class": "navbar-brand", "href": href}, [name])


def navbar_nav_left(content: HeavymetalDynamicContent) -> Heavymetal:
    return ul({"class": "navbar-nav me-auto"}, content)


def navbar_nav_right(content: HeavymetalDynamicContent) -> Heavymetal:
    return ul({"class": "navbar-nav ms-auto"}, content)


def navbar_toggler(content: HeavymetalDynamicContent) -> Heavymetal:
    navbar_collapse_id = "navbar-content"
    return fragment([
        button(
            {
                "class": "navbar-toggler",
                "type": "button",
                "data-bs-toggle": "collapse",
                "data-bs-target": f"#{navbar_collapse_id}",
                "aria-controls": f"{navbar_collapse_id}",
                "aria-expanded": "false",
                "aria-label": "Toggle navigation",
            },
            [span({"class": "navbar-toggler-icon"}, ())],
        ),
        div({"class": "collapse navbar-collapse", "id": navbar_collapse_id}, content),
    ])


def nav_item(name: str, href: str, active_page: bool = False) -> Heavymetal:
    if active_page:
        content = a({"class": "nav-link active", "aria-current": "page", "href": href}, [name])
    else:
        content = a({"class": "nav-link", "href": href}, [name])

    return ("li", {"class": "nav-item"}, [content])


def nav_item_dropdown(name: str, menu: typing.Sequence[DropdownItem | DropdownDivider], end: bool = False) -> Heavymetal:
    """
    <li class="nav-item dropdown">
      <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
        Dropdown
      </a>
      <ul class="dropdown-menu">
        <li><a class="dropdown-item" href="#">Action</a></li>
        <li><a class="dropdown-item" href="#">Another action</a></li>
        <li><hr class="dropdown-divider"></li>
        <li><a class="dropdown-item" href="#">Something else here</a></li>
      </ul>
    </li>
    """

    dropdown_toggle = a(
        {
            "class": "nav-link dropdown-toggle",
            "href": "#",
            "role": "button",
            "data-bs-toggle": "dropdown",
            "aria-expanded": "false",
        },
        [name],
    )
    dropdown_menu = ul({"class": html_classes({"dropdown-menu": True, "dropdown-menu-end": end})}, tuple(menu))
    return ("li", {"class": "nav-item dropdown"}, [dropdown_toggle, dropdown_menu])


def dropdown_item(name: str, href: str, active: bool = None) -> DropdownItem:
    return ("li", {}, [a({"class": html_classes("dropdown-item", {"active": active}), "href": href}, [name])])


def dropdown_divider() -> DropdownDivider:
    return ("li", {"class": "dropdown-divider"}, ())
