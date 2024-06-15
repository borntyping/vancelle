import dataclasses
import typing

import flask
import flask_login
import sqlalchemy

from vancelle.extensions import db
from vancelle.lib.heavymetal import Heavymetal, HeavymetalComponent
from vancelle.lib.heavymetal.html import a, div, h1, section
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
        return div(
            {"class": f"card h-100 text-center bg-{self.colour}-subtle text-{self.colour}-emphasis"},
            [
                div(
                    {"class": "card-body"},
                    [
                        div({"class": "display-3"}, [str(self.count)]),
                        a(
                            {
                                "class": "card-title stretched-link text-decoration-none",
                                "href": self.href,
                            },
                            [self.title],
                        ),
                    ],
                )
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
            yield HomePageGauge(count, cls.info.noun_plural_title, url, "info")

        for cls, count in self._count_by_type(Remote).items():
            url = flask.url_for("work.index", remote_type=cls.remote_type())
            yield HomePageGauge(count, cls.info.noun_full_plural, url, cls.info.colour)

    def heavymetal(self) -> Heavymetal:
        gauges = sorted(self, key=lambda g: g.count, reverse=True)
        return div(
            {"class": "my-5 row row-cols-1 row-cols-lg-4 row-cols-xxl-5 g-4 justify-content-center"},
            [div({"class": "col"}, [g]) for g in gauges],
        )


class HomePageHero(HeavymetalComponent):
    categories: list[str] = [cls.info.noun_plural for cls in Work.iter_subclasses()]

    def heavymetal(self) -> Heavymetal:
        return section(
            {"class": "text-center"},
            [
                h1({"class": "display-1 fw-bold"}, "Vancelle"),
                ("p", {"class": "display-6 mb-4"}, f"Track {p.join(self.categories)}"),
            ],
        )


@dataclasses.dataclass()
class HomePage(HeavymetalComponent):
    def heavymetal(self) -> Heavymetal:
        return page([HomePageHero(), HomePageGauges()], title=())
