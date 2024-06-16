import flask
import flask_login

from vancelle.ext.flask import url_is_active
from vancelle.html.bootstrap.components.navbar import (
    dropdown_divider,
    dropdown_item,
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
                _page_dropdown_item(cls.info.noun_plural_title, "work.index", work_type=cls.work_type())
                for cls in Work.iter_subclasses()
            ),
        ],
    )


def _new_works_dropdown() -> Heavymetal:
    return nav_item_dropdown(
        "Add new work",
        [
            _page_dropdown_item("Create new work", "work.create"),
            dropdown_divider(),
            *(
                _page_dropdown_item(remote_type.info.noun_full, "remote.search_source", remote_type=remote_type)
                for remote_type in Remote.iter_subclasses_interactive()
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


def page_navbar() -> Heavymetal:
    return navbar(
        navbar_brand(name="Vancelle", href=flask.url_for("home.home")),
        [
            _works_dropdown(),
            _new_works_dropdown(),
        ],
        [
            _user_dropdown(),
        ],
    )
