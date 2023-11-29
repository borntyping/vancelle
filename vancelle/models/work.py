import dataclasses
import datetime
import math
import typing
import uuid

from flask import url_for
from sqlalchemy import Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .details import Details, IntoDetails
from .record import Record
from .remote import Remote
from .types import ShelfEnum
from .user import User
from ..inflect import p
from ..shelf import Shelf


@dataclasses.dataclass()
class WorkInfo:
    noun: str
    title: str
    plural: str
    priority: int

    def __init__(self, noun: str, *, title: str | None = None, plural: str | None = None, priority: int) -> None:
        self.noun = noun
        self.title = title or noun.title()
        self.plural = plural or p.plural(noun)
        self.priority = priority


class Work(Base, IntoDetails):
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
    shelf: Mapped[typing.Optional[Shelf]] = mapped_column(ShelfEnum, default=None)
    tags: Mapped[typing.Optional[set[str]]] = mapped_column(ARRAY(String), default=None)

    records: Mapped[typing.List["Record"]] = relationship(
        back_populates="work",
        order_by="Record.date_stopped, Record.date_started, Record.time_created",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    remotes: Mapped[typing.List["Remote"]] = relationship(
        back_populates="work",
        order_by="Remote.id",
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
            external_url=None,
        )

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
            shelf=next((d.shelf for d in details if d.shelf), Shelf.UNSORTED),
            external_url=None,
        )

    @classmethod
    def identity(cls) -> str:
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
    info = WorkInfo(noun="book", priority=1)


class Game(Work):
    __mapper_args__ = {"polymorphic_identity": "game"}
    info = WorkInfo(noun="game", priority=2)


class Film(Work):
    __mapper_args__ = {"polymorphic_identity": "film"}
    info = WorkInfo(noun="film", priority=3)


class Show(Work):
    __mapper_args__ = {"polymorphic_identity": "show"}
    info = WorkInfo(noun="show", priority=4)


class Music(Work):
    __mapper_args__ = {"polymorphic_identity": "music"}
    info = WorkInfo(noun="music", plural="music", priority=5)


class BoardGame(Work):
    __mapper_args__ = {"polymorphic_identity": "boardgame"}
    info = WorkInfo(noun="board game", priority=6)
