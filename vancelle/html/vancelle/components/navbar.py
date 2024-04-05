import flask
import flask_login

from vancelle.ext.flask import url_is_active
from vancelle.html.bulma.components.navbar import (
    navbar,
    navbar_brand,
    navbar_divider,
    navbar_item,
    navbar_item_dropdown,
    navbar_menu,
)
from vancelle.html.hotmetal import Hotmetal
from vancelle.models import Remote, Work


def _page_navbar_item(title: str, endpoint: str, **values: str) -> Hotmetal:
    href = flask.url_for(endpoint, **values)
    active = url_is_active(endpoint, **values)
    return navbar_item(title=title, href=href, active=active)


def _works_dropdown() -> Hotmetal:
    return navbar_item_dropdown(
        "Works",
        _page_navbar_item("All", "work.index"),
        navbar_divider(),
        *(
            _page_navbar_item(cls.info.noun_plural_title, "work.index", work_type=cls.work_type())
            for cls in Work.iter_subclasses()
        ),
    )


def _new_works_dropdown() -> Hotmetal:
    return navbar_item_dropdown(
        "Add new work",
        _page_navbar_item("Create new work", "work.create"),
        navbar_divider(),
        *(
            _page_navbar_item(cls.info.noun_full, "remote.search_source", remote_type=cls.remote_type())
            for cls in Remote.filter_subclasses(can_search=True)
        ),
    )


def _user_dropdown() -> Hotmetal:
    if not flask_login.current_user.is_authenticated:
        return _page_navbar_item("Login", "user.login")

    return navbar_item_dropdown(
        f"Logged in as {flask_login.current_user.username}",
        _page_navbar_item("Import/export data", "user.profile"),
        _page_navbar_item("Manage remote data", "remote.index"),
        _page_navbar_item("Manage cached data", "cache.index"),
        _page_navbar_item("Logout", "user.logout"),
        is_right=True,
    )


def page_navbar() -> Hotmetal:
    return navbar(
        navbar_brand(name="Vancelle", href=flask.url_for("work.home")),
        navbar_menu(start=[_works_dropdown(), _new_works_dropdown()], end=[_user_dropdown()]),
    )
