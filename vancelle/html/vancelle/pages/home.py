import typing

import flask

from vancelle.controllers.work import Gauge
from vancelle.html.types import Hotmetal
from vancelle.inflect import p
from .base import base
from ...helpers import html_classes


def home_page_hero(categories: typing.Sequence[str]) -> Hotmetal:
    return (
        "section",
        {"class": "hero is-medium is-primary"},
        [
            (
                "div",
                {"class": "hero-body has-text-centered"},
                [
                    ("h1", {"class": "title is-2"}, "Vancelle"),
                    ("p", {"class": "subtitle is-4"}, f"Track {p.join(categories)}"),
                    ("a", {"class": "button is-large is-link mx-3", "href": flask.url_for("work.index")}, ["View works"]),
                    ("a", {"class": "button is-large is-link mx-3", "href": flask.url_for("work.create")}, ["Add work"]),
                ],
            )
        ],
    )


def home_page_gauges(gauges: typing.Sequence[Gauge]) -> Hotmetal:
    return (
        "section",
        {"class": "section"},
        [
            (
                "div",
                {"class": "x-gauges"},
                [
                    (
                        "a",
                        {
                            "href": gauge.href,
                            "class": html_classes(
                                "x-gauge",
                                f"has-background-{gauge.colour}-soft",
                                f"has-text-{gauge.colour}-bold",
                            ),
                        },
                        [
                            ("div", {"class": "is-size-1"}, [str(gauge.count)]),
                            ("div", {"class": ""}, [gauge.title]),
                        ],
                    )
                    for gauge in gauges
                ],
            )
        ],
    )


def home_page(categories: typing.Sequence[str], gauges: typing.Sequence[Gauge]) -> Hotmetal:
    return base(before=home_page_hero(categories), content=home_page_gauges(gauges))
