import dataclasses
import typing

import flask
import flask_login
import sqlalchemy

from vancelle.extensions import db
from vancelle.lib.heavymetal import Heavymetal, HeavymetalComponent
from vancelle.lib.heavymetal.html import a, div, section
from vancelle.html.helpers import html_classes
from vancelle.inflect import p
from vancelle.models import User
from vancelle.models.remote import Remote
from vancelle.models.work import Work
from .base import page


@dataclasses.dataclass()
class HomePageGauge(HeavymetalComponent):
    count: int
    title: str
    href: str
    colour: str

    def heavymetal(self) -> Heavymetal:
        return a(
            {
                "href": self.href,
                "class": html_classes(
                    "box",
                    f"has-background-{self.colour}-soft",
                    f"has-text-{self.colour}-bold",
                    "x-gauge",
                    "has-text-centered",
                ),
            },
            [
                ("div", {"class": "is-size-2-touch is-size-1-desktop"}, [str(self.count)]),
                ("div", {}, [self.title]),
            ],
        )


class HomePageGauges(HeavymetalComponent):
    def _count_works(self) -> int:
        query = (
            sqlalchemy.select(sqlalchemy.func.count())
            .select_from(Work)
            .join(User)
            .filter(User.id == flask_login.current_user.id)
        )
        return db.session.execute(query).scalar_one()

    def _count_remotes(self) -> int:
        query = (
            sqlalchemy.select(sqlalchemy.func.count())
            .select_from(Remote)
            .join(Work)
            .join(User)
            .filter(User.id == flask_login.current_user.id)
        )
        return db.session.execute(query).scalar_one()

    def _count_by_type(self, cls: typing.Type[Work | Remote]) -> dict[typing.Type[Work | Remote], int]:
        subclasses = cls.iter_subclasses()

        count = sqlalchemy.func.count().label("count")
        stmt = sqlalchemy.select(cls.type, count).select_from(cls).order_by(count.desc()).group_by(cls.type)

        results = {t: c for t, c in db.session.execute(stmt)}
        return {s: r for s in subclasses if (r := results.get(s.__mapper__.polymorphic_identity, 0))}

    def __iter__(self) -> typing.Iterator[HomePageGauge]:
        works = self._count_works()
        yield HomePageGauge(works, p.plural("Work", works), flask.url_for("work.index"), "primary")

        remotes = self._count_remotes()
        yield HomePageGauge(remotes, p.plural("Remote", remotes), flask.url_for("remote.index"), "primary")

        for cls, count in self._count_by_type(Work).items():
            url = flask.url_for("work.index", work_type=cls.work_type())
            yield HomePageGauge(count, cls.info.noun_plural_title, url, "link")

        for cls, count in self._count_by_type(Remote).items():
            url = flask.url_for("work.index", remote_type=cls.remote_type())
            yield HomePageGauge(count, cls.info.noun_full_plural, url, cls.info.colour)

    def heavymetal(self) -> Heavymetal:
        gauges = sorted(self, key=lambda g: g.count, reverse=True)
        return div(
            {"class": "columns is-multiline is-mobile is-centered"},
            [div({"class": "column is-half-mobile is-one-fifth-desktop"}, [g]) for g in gauges],
        )


class HomePageHero(HeavymetalComponent):
    categories: list[str] = [cls.info.noun_plural for cls in Work.iter_subclasses()]

    def heavymetal(self) -> Heavymetal:
        return section(
            {"class": "hero is-medium is-primary"},
            [
                div(
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


@dataclasses.dataclass()
class HomePage(HeavymetalComponent):
    def heavymetal(self) -> Heavymetal:
        return page(HomePageGauges(), before=HomePageHero())
