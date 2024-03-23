import dataclasses
import datetime
import typing
import uuid

from flask import url_for
from sqlalchemy import ForeignKey, String, asc, func, nulls_last
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import coalesce

from .base import PolymorphicBase
from .details import Details, IntoDetails
from .properties import IntoProperties, Property, StringProperty, TimeProperty
from .record import Record
from .remote import Remote
from .types import ShelfEnum
from .user import User
from ..inflect import p
from ..shelf import Shelf


@dataclasses.dataclass()
class WorkInfo:
    slug: str
    noun: str
    noun_title: str
    noun_plural: str
    noun_plural_title: str
    priority: int

    def __init__(
        self,
        slug: str,
        noun: str,
        *,
        noun_title: str | None = None,
        plural: str | None = None,
        plural_title: str | None = None,
        priority: int,
    ) -> None:
        self.slug = slug
        self.noun = noun
        self.noun_title = noun_title or self.noun.title()
        self.noun_plural = plural or p.plural(self.noun)
        self.noun_plural_title = plural_title or self.noun_plural.title()
        self.priority = priority

    def plural(self, count: int) -> str:
        return self.noun if count == 1 else self.noun_plural

    def plural_title(self, count: int) -> str:
        return self.noun_title if count == 1 else self.noun_plural_title


class Work(PolymorphicBase, IntoDetails, IntoProperties):
    __tablename__ = "work"
    __mapper_args__ = {"polymorphic_on": "type"}

    info: typing.ClassVar[WorkInfo]

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User] = relationship(back_populates="works")

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String)

    time_created: Mapped[datetime.datetime] = mapped_column(default=func.now(), insert_default=func.now())
    time_updated: Mapped[typing.Optional[datetime.datetime]] = mapped_column(default=None, onupdate=func.now())
    time_deleted: Mapped[typing.Optional[datetime.datetime]] = mapped_column(default=None)

    title: Mapped[typing.Optional[str]] = mapped_column(default=None)
    author: Mapped[typing.Optional[str]] = mapped_column(default=None)
    series: Mapped[typing.Optional[str]] = mapped_column(default=None)
    description: Mapped[typing.Optional[str]] = mapped_column(default=None)
    release_date: Mapped[typing.Optional[datetime.date]] = mapped_column(default=None)
    cover: Mapped[typing.Optional[str]] = mapped_column(default=None)
    background: Mapped[typing.Optional[str]] = mapped_column(default=None)
    shelf: Mapped[Shelf] = mapped_column(ShelfEnum, default=Shelf.UNSORTED)
    tags: Mapped[typing.Optional[set[str]]] = mapped_column(ARRAY(String), default=None)
    external_url: Mapped[typing.Optional[str]] = mapped_column(default=None)

    records: Mapped[typing.List["Record"]] = relationship(
        back_populates="work",
        order_by=nulls_last(asc(coalesce(Record.date_started, Record.date_stopped))),
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    remotes: Mapped[typing.List["Remote"]] = relationship(
        back_populates="work",
        order_by="desc(Remote.id)",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def deleted(self) -> bool:
        return self.time_deleted is not None

    def get_record(self) -> typing.Optional["Record"]:
        return next((r for r in reversed(self.records) if not r.deleted), None)

    @property
    def record(self) -> typing.Optional["Record"]:
        return self.get_record() or Record(work=self)

    @property
    def date_started(self) -> datetime.date | None:
        if records := [r for r in self.records if r.date_started and not r.deleted]:
            return min(r.date_started for r in records)
        return None

    @property
    def date_stopped(self) -> datetime.date | None:
        if records := [r for r in self.records if r.date_stopped and not r.deleted]:
            return max(r.date_stopped for r in records)
        return None

    def url_for(self) -> str:
        return url_for("work.detail", work_id=self.id)

    def url_for_cover(self) -> str | None:
        return url_for("work.cover", work_id=self.id) if self.cover else None

    def url_for_background(self) -> str | None:
        return url_for("work.background", work_id=self.id) if self.background else None

    def iter_remotes(self) -> typing.Iterable["Remote"]:
        return reversed(sorted(self.remotes, key=lambda remote: remote.info.priority))

    def iter_active_remotes(self) -> typing.Iterable["Remote"]:
        return (remote for remote in self.iter_remotes() if not remote.deleted)

    def into_details(self) -> Details:
        return Details(
            title=self.title,
            author=self.author,
            series=self.series,
            description=self.description,
            release_date=self.release_date,
            cover=self.url_for_cover(),
            background=self.url_for_background(),
            tags=self.tags,
            external_url=self.external_url,
        )

    def into_properties(self) -> typing.Iterable[Property]:
        yield StringProperty("ID", self.id)
        yield StringProperty("Type", self.info.noun_title)
        yield TimeProperty("Created", self.time_created)
        yield TimeProperty("Updated", self.time_updated)
        yield TimeProperty("Deleted", self.time_deleted)

    def resolve_details(self) -> Details:
        """Collapse the chain into a single Details instance, including details from the work."""
        items: list[IntoDetails] = [self, *self.iter_active_remotes()]
        details = [item.into_details() for item in items]
        return Details(
            title=next((d.title for d in details if d.title), None),
            author=next((d.author for d in details if d.author), None),
            series=next((d.series for d in details if d.series), None),
            description=next((d.description for d in details if d.description), None),
            release_date=next((d.release_date for d in details if d.release_date), None),
            cover=next((d.cover for d in details if d.cover), None),
            background=next((d.background for d in details if d.background), None),
            tags=next((d.tags for d in details if d.tags), set()),
            external_url=next((d.external_url for d in details if d.external_url), None),
        )

    @classmethod
    def work_type(cls) -> str:
        return cls.polymorphic_identity()


class Book(Work):
    __mapper_args__ = {"polymorphic_identity": "book"}
    info = WorkInfo(slug="books", noun="book", priority=10)


class Game(Work):
    __mapper_args__ = {"polymorphic_identity": "game"}
    info = WorkInfo(slug="games", noun="game", priority=9)


class Film(Work):
    __mapper_args__ = {"polymorphic_identity": "film"}
    info = WorkInfo(slug="films", noun="film", priority=8)


class Show(Work):
    __mapper_args__ = {"polymorphic_identity": "show"}
    info = WorkInfo(slug="shows", noun="show", priority=7)


class Album(Work):
    __mapper_args__ = {"polymorphic_identity": "music"}
    info = WorkInfo(slug="album", noun="album", priority=6)


class TabletopGame(Work):
    __mapper_args__ = {"polymorphic_identity": "boardgame"}
    info = WorkInfo(slug="tabletop-games", noun="tabletop game", noun_title="Tabletop game", priority=5)
