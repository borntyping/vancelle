import dataclasses
import datetime
import typing
import uuid

from flask import url_for
from sqlalchemy import Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .metadata import Details, IntoDetails
from .record import Record
from .remote import Remote
from .user import User
from ..inflect import p
from ..types import Shelf


@dataclasses.dataclass()
class WorkInfo:
    noun: str
    title: str
    plural: str

    def __init__(self, noun: str, *, title: str = None, plural: str = None) -> None:
        self.noun = noun
        self.title = title or noun
        self.plural = plural or p.plural(noun)


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
    shelf: Mapped[typing.Optional[Shelf]] = mapped_column(Enum(Shelf, native_enum=False, validate_strings=True), default=None)
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
        return next((r for r in self.records if not r.deleted), None)

    @property
    def record(self) -> typing.Optional["Record"]:
        return self.get_record() or Record(work=self)

    def url_for(self) -> str:
        return url_for("work.detail", work_id=self.id)

    def iter_remotes(self) -> typing.Iterable["Remote"]:
        return reversed(sorted(self.remotes, key=lambda remote: remote.into_source().priority))

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
        )

    def _resolve_details(self, *chain: IntoDetails) -> Details:
        chain = [item.into_details() for item in chain]
        return Details(
            title=next((d.title for d in chain if d.title), None),
            author=next((d.author for d in chain if d.author), None),
            description=next((d.description for d in chain if d.description), None),
            release_date=next((d.release_date for d in chain if d.release_date), None),
            cover=next((d.cover for d in chain if d.cover), None),
            background=next((d.background for d in chain if d.background), None),
            tags=next((d.tags for d in chain if d.tags), {}),
            shelf=next((d.shelf for d in chain if d.shelf), Shelf.UNSORTED),
        )

    def resolve_remote_details(self) -> Details:
        """
        Collapse the chain into a single Details instance, only using remote details.
        The only appropriate place to use this is the update form.
        """
        return self._resolve_details(*self.iter_active_remotes())

    def resolve_details(self) -> Details:
        """Collapse the chain into a single Details instance, including details from the work."""
        return self._resolve_details(self, *self.iter_active_remotes())

    def linkable_remotes(self) -> typing.Mapping[str, typing.Type["Remote"]]:
        present_remotes = {remote.type: remote for remote in self.remotes}
        absent_remotes = {
            remote_type: remote_cls
            for remote_type, remote_cls in Remote.subclasses().items()
            if remote_type not in present_remotes and remote_cls.into_source().can_link
        }
        return absent_remotes

    @classmethod
    def subclasses(cls) -> typing.Mapping[str, typing.Type["Work"]]:
        return {identity: mapper.class_ for identity, mapper in cls.__mapper__.polymorphic_map.items()}


class Book(Work):
    __mapper_args__ = {"polymorphic_identity": "book"}
    info = WorkInfo(noun="book")


class Game(Work):
    __mapper_args__ = {"polymorphic_identity": "game"}
    info = WorkInfo(noun="game")


class Film(Work):
    __mapper_args__ = {"polymorphic_identity": "film"}
    info = WorkInfo(noun="film")


class Show(Work):
    __mapper_args__ = {"polymorphic_identity": "show"}
    info = WorkInfo(noun="show")


class Music(Work):
    __mapper_args__ = {"polymorphic_identity": "music"}
    info = WorkInfo(noun="music", plural="music")


class BoardGame(Work):
    __mapper_args__ = {"polymorphic_identity": "boardgame"}
    info = WorkInfo(noun="board game")
