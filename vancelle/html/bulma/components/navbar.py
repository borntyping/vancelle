import typing

from vancelle.html.helpers import html_classes
from vancelle.html.types import Hotmetal, Href


def navbar(brand: Hotmetal, menu: Hotmetal) -> Hotmetal:
    return (
        "nav",
        {"class": "navbar is-primary"},
        [
            (
                "div",
                {"class": "container"},
                [
                    brand,
                    menu,
                ],
            )
        ],
    )


def navbar_brand(name: str, href: Href) -> Hotmetal:
    return (
        "div",
        {"class": "navbar-brand"},
        [
            ("a", {"class": "navbar-item has-text-weight-bold", "href": str(href)}, [name]),
            navbar_burger(),
        ],
    )


def navbar_burger() -> Hotmetal:
    return (
        "a",
        {"class": "navbar-burger", "_": "on click toggle .is-active on .navbar-menu"},
        [
            ("span", {"aria-hidden": "true"}, []),
            ("span", {"aria-hidden": "true"}, []),
            ("span", {"aria-hidden": "true"}, []),
        ],
    )


def navbar_menu(start: typing.Iterable[Hotmetal], end: typing.Iterable[Hotmetal]) -> Hotmetal:
    return (
        "div",
        {"class": "navbar-menu"},
        [
            ("div", {"class": "navbar-start"}, list(start)),
            ("div", {"class": "navbar-end"}, list(end)),
        ],
    )


def navbar_item(title: str, href: Href, active: bool = False) -> Hotmetal:
    return ("a", {"class": html_classes("navbar-item", {"is-active": active}), "href": str(href)}, [title])


def navbar_item_dropdown(name: str, items: typing.Iterable[Hotmetal]) -> Hotmetal:
    return (
        "div",
        {
            "class": html_classes("navbar-item", "is-hoverable", "has-dropdown", {"is-active": False}),
            "_": "on click toggle .is-active",
        },
        [
            ("span", {"class": "navbar-link"}, [name]),
            ("div", {"class": "navbar-dropdown"}, items),
        ],
    )


def navbar_divider() -> Hotmetal:
    return ("hr", {"class": "navbar-divider"}, [])
