import dataclasses
import typing

import flask

from vancelle.controllers.work import Gauge
from vancelle.html.hotmetal import Hotmetal, HotmetalClass
from vancelle.inflect import p
from .base import page
from ...helpers import html_classes


@dataclasses.dataclass()
class HomePage(HotmetalClass):
    categories: typing.Sequence[str]
    gauges: typing.Sequence[Gauge]

    def __call__(self, context: typing.Any) -> Hotmetal:
        return page(self._gauges(), before=self._hero())

    def _hero(self) -> Hotmetal:
        return (
            "section",
            {"class": "hero is-medium is-primary"},
            [
                (
                    "div",
                    {"class": "hero-body has-text-centered"},
                    [
                        ("h1", {"class": "title is-2"}, "Vancelle"),
                        ("p", {"class": "subtitle is-4"}, f"Track {p.join(self.categories)}"),
                        ("a", {"class": "button is-large is-link m-2", "href": flask.url_for("work.index")}, ["View works"]),
                        ("a", {"class": "button is-large is-link m-2", "href": flask.url_for("work.create")}, ["Add work"]),
                    ],
                )
            ],
        )

    def _gauges(self) -> Hotmetal:
        return ("div", {"class": "columns is-multiline is-mobile x-gauges"}, [self._gauge(g) for g in self.gauges])

    def _gauge(self, gauge: Gauge) -> Hotmetal:
        return (
            "div",
            {"class": "column is-half-mobile is-one-fifth-desktop"},
            [
                (
                    "a",
                    {
                        "href": gauge.href,
                        "class": html_classes(
                            "box",
                            f"has-background-{gauge.colour}-soft",
                            f"has-text-{gauge.colour}-bold",
                            "x-gauge",
                            "has-text-centered",
                        ),
                    },
                    [
                        ("div", {"class": "is-size-2-touch is-size-1-desktop"}, [str(gauge.count)]),
                        ("div", {}, [gauge.title]),
                    ],
                )
            ],
        )
