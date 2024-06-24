import typing

import flask
import flask_login

from vancelle.controllers.sources import Source
from vancelle.ext.flask import url_is_active
from vancelle.html.bootstrap.components.navbar import (
    dropdown_divider,
    dropdown_item,
    nav_item_dropdown,
    navbar,
    navbar_brand,
)
from vancelle.lib.heavymetal import Heavymetal
from vancelle.models import Entry, Work


def _DropdownItem(title: str, endpoint: str, **values: str) -> Heavymetal:
    href = flask.url_for(endpoint, **values)
    active = url_is_active(endpoint, **values)
    return dropdown_item(name=title, href=href, active=active)


def _BoardDropdown() -> Heavymetal:
    return nav_item_dropdown(
        "Board",
        [
            _DropdownItem("All", "board.index"),
            dropdown_divider(),
            *(
                _DropdownItem(cls.info.noun_plural_title, "board.index", type=cls.polymorphic_identity())
                for cls in Work.subclasses()
            ),
        ],
    )


def _WorkDropdown() -> Heavymetal:
    return nav_item_dropdown(
        "Works",
        [
            _DropdownItem("All", "work.index"),
            dropdown_divider(),
            *(
                _DropdownItem(cls.info.noun_plural_title, "work.index", type=cls.polymorphic_identity())
                for cls in Work.subclasses()
            ),
        ],
    )


def _EntryDropdown() -> Heavymetal:
    return nav_item_dropdown(
        "Entries",
        [
            _DropdownItem("All", "entry.index"),
            dropdown_divider(),
            *(
                _DropdownItem(cls.info.noun_full, "entry.index", entry_type=cls.polymorphic_identity())
                for cls in Entry.subclasses()
            ),
        ],
    )


def _NewWorksDropdown(sources: typing.Sequence[Source]) -> Heavymetal:
    return nav_item_dropdown(
        "Add new work",
        [
            _DropdownItem("Create new work", "work.create"),
            dropdown_divider(),
            *(
                _DropdownItem(source.name, "source.search", entry_type=source.polymorphic_identity())
                for source in Source.subclasses()
            ),
        ],
    )


def _UserDropdown() -> Heavymetal:
    if not flask_login.current_user.is_authenticated:
        return _DropdownItem("Login", "user.login")

    return nav_item_dropdown(
        f"Logged in as {flask_login.current_user.username}",
        [
            _DropdownItem("Manage data", "user.settings"),
            _DropdownItem("Logout", "user.logout"),
        ],
        True,
    )


def PageNavbar(sources: typing.Sequence[Source]) -> Heavymetal:
    return navbar(
        navbar_brand(name="Vancelle", href=flask.url_for("home.home")),
        [
            _BoardDropdown(),
            _WorkDropdown(),
            _EntryDropdown(),
            _NewWorksDropdown(sources=sources),
        ],
        [
            _UserDropdown(),
        ],
    )
