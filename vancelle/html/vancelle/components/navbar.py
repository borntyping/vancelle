import flask

from vancelle.ext.flask import url_is_active
from vancelle.html.bulma.components.navbar import navbar, navbar_brand, navbar_item, navbar_menu
from vancelle.html.types import Hotmetal


def page_navbar_item(title: str, endpoint: str, **values: str) -> Hotmetal:
    href = flask.url_for(endpoint, **values)
    active = url_is_active(endpoint, **values)
    return navbar_item(title=title, href=href, active=active)


def page_navbar() -> Hotmetal:
    return navbar(
        navbar_brand(name="Vancelle", href=flask.url_for("work.home")),
        navbar_menu(
            start=[],
            end=[
                # page_navbar_item(request, "Home", name="home"),
                # page_navbar_item(request, "Error", name="error"),
            ],
        ),
    )
