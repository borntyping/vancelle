import typing

from vancelle.lib.html import html_classes
from vancelle.lib.heavymetal import Heavymetal


def navbar(brand: Heavymetal, menu: Heavymetal) -> Heavymetal:
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


def navbar_brand(name: str, href: str) -> Heavymetal:
    return (
        "div",
        {"class": "navbar-brand"},
        [
            ("a", {"class": "navbar-item has-text-weight-bold", "href": href}, [name]),
            navbar_burger(),
        ],
    )


def navbar_burger() -> Heavymetal:
    return (
        "a",
        {"class": "navbar-burger", "_": "on click toggle .is-active on .navbar-menu"},
        [
            ("span", {"aria-hidden": "true"}, []),
            ("span", {"aria-hidden": "true"}, []),
            ("span", {"aria-hidden": "true"}, []),
        ],
    )


def navbar_menu(start: typing.Iterable[Heavymetal], end: typing.Iterable[Heavymetal]) -> Heavymetal:
    return (
        "div",
        {"class": "navbar-menu"},
        [
            ("div", {"class": "navbar-start"}, list(start)),
            ("div", {"class": "navbar-end"}, list(end)),
        ],
    )


def navbar_item(title: str, href: str, active: bool = False) -> Heavymetal:
    return ("a", {"class": html_classes("navbar-item", {"is-active": active}), "href": href}, [title])


def navbar_item_dropdown(name: str, *items: typing.Iterable[Heavymetal], is_right: bool = False) -> Heavymetal:
    return (
        "div",
        {
            "class": html_classes("navbar-item", "has-dropdown", {"is-active": False}),
            "_": "on click toggle .is-active",
        },
        [
            ("span", {"class": "navbar-link"}, [name]),
            ("div", {"class": html_classes("navbar-dropdown", {"is-right": is_right})}, items),
        ],
    )


def navbar_divider() -> Heavymetal:
    return ("hr", {"class": "navbar-divider"}, [])
