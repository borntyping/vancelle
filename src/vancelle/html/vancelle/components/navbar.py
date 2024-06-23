import typing

import flask
import flask_login

from vancelle.controllers.sources import Source
from vancelle.ext.flask import url_is_active
from vancelle.html.bootstrap.components.navbar import (
    dropdown_divider,
    dropdown_item,
    nav_item,
    nav_item_dropdown,
    navbar,
    navbar_brand,
)
from vancelle.lib.heavymetal import Heavymetal
from vancelle.models import Remote, Work


def _page_dropdown_item(title: str, endpoint: str, **values: str) -> Heavymetal:
    href = flask.url_for(endpoint, **values)
    active = url_is_active(endpoint, **values)
    return dropdown_item(name=title, href=href, active=active)


def _works_dropdown() -> Heavymetal:
    return nav_item_dropdown(
        "Works",
        [
            _page_dropdown_item("All", "work.index"),
            dropdown_divider(),
            *(
                _page_dropdown_item(cls.info.noun_plural_title, "work.index", type=cls.work_type())
                for cls in Work.iter_subclasses()
            ),
        ],
    )


def _remotes_dropdown() -> Heavymetal:
    return nav_item_dropdown(
        "Remotes",
        [
            _page_dropdown_item("All", "remote.index"),
            dropdown_divider(),
            *(
                _page_dropdown_item(cls.info.noun_full, "remote.index", type=cls.remote_type())
                for cls in Remote.iter_subclasses()
            ),
        ],
    )


def _new_works_dropdown(sources: typing.Sequence[Source]) -> Heavymetal:
    return nav_item_dropdown(
        "Add new work",
        [
            _page_dropdown_item("Create new work", "work.create"),
            dropdown_divider(),
            *(
                _page_dropdown_item(source.name, "source.search", remote_type=source.remote_type.polymorphic_identity())
                for source in sources
            ),
        ],
    )


def _user_dropdown() -> Heavymetal:
    if not flask_login.current_user.is_authenticated:
        return _page_dropdown_item("Login", "user.login")

    return nav_item_dropdown(
        f"Logged in as {flask_login.current_user.username}",
        [
            _page_dropdown_item("Manage data", "user.settings"),
            _page_dropdown_item("Logout", "user.logout"),
        ],
        True,
    )


def PageNavbar(sources: typing.Sequence[Source]) -> Heavymetal:
    return navbar(
        navbar_brand(name="Vancelle", href=flask.url_for("home.home")),
        [
            nav_item("Board", flask.url_for("board.index"), url_is_active("board.index")),
            _works_dropdown(),
            _new_works_dropdown(sources=sources),
            _remotes_dropdown(),
        ],
        [
            _user_dropdown(),
        ],
    )
