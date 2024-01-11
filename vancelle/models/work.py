import dataclasses
import datetime
import math
import typing
import uuid

from flask import url_for
from sqlalchemy import Enum, ForeignKey, String, asc, desc, func, nulls_last
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import coalesce

from .base import Base
from .details import Details, IntoDetails, IntoProperties, Property, StringProperty, TimeProperty
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
    plural: str
    plural_title: str
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
        self.plural = plural or p.plural(self.noun)
        self.plural_title = plural_title or self.plural.title()
        self.priority = priority


class Work(Base, IntoDetails, IntoProperties):
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

    def iter_remotes(self) -> typing.Iterable["Remote"]:
        return reversed(sorted(self.remotes, key=lambda remote: remote.info.priority))

    def iter_active_remotes(self) -> typing.Iterable["Remote"]:
        return (remote for remote in self.iter_remotes() if not remote.deleted)

    def into_details(self) -> Details:
        return Details(
            title=self.title,
            author=self.author,
            description=self.description,
            release_date=self.release_date,
            cover=self.cover,
            background=self.background,
            shelf=self.shelf,
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
            description=next((d.description for d in details if d.description), None),
            release_date=next((d.release_date for d in details if d.release_date), None),
            cover=next((d.cover for d in details if d.cover), None),
            background=next((d.background for d in details if d.background), None),
            tags=next((d.tags for d in details if d.tags), set()),
            shelf=self.shelf,
            external_url=next((d.external_url for d in details if d.external_url), None),
        )

    @classmethod
    def work_type(cls) -> str:
        assert cls.__mapper__.polymorphic_identity is not None
        return cls.__mapper__.polymorphic_identity

    @classmethod
    def iter_subclasses(cls) -> typing.Sequence[typing.Type["Work"]]:
        return list(
            sorted(
                (mapper.class_ for mapper in cls.__mapper__.polymorphic_map.values()),
                key=lambda c: c.info.priority,
            )
        )


class Book(Work):
    __mapper_args__ = {"polymorphic_identity": "book"}
    info = WorkInfo(slug="books", noun="book", priority=1)


class Game(Work):
    __mapper_args__ = {"polymorphic_identity": "game"}
    info = WorkInfo(slug="games", noun="game", priority=2)


class Film(Work):
    __mapper_args__ = {"polymorphic_identity": "film"}
    info = WorkInfo(slug="films", noun="film", priority=3)


class Show(Work):
    __mapper_args__ = {"polymorphic_identity": "show"}
    info = WorkInfo(slug="shows", noun="show", priority=4)


class Music(Work):
    __mapper_args__ = {"polymorphic_identity": "music"}
    info = WorkInfo(slug="music", noun="music", plural="music", priority=5)


class TabletopGame(Work):
    __mapper_args__ = {"polymorphic_identity": "boardgame"}
    info = WorkInfo(slug="tabletop-games", noun="tabletop game", noun_title="Tabletop game", priority=6)
