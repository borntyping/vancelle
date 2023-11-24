import functools
import typing
from datetime import date, datetime
from typing import Iterable, List, Mapping, Optional, Type, TypeVar, TypedDict
from uuid import UUID

from flask import url_for
from flask_login import UserMixin
from sqlalchemy import ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from vancelle.clients.goodreads.types import GoodreadsCsvRow, GoodreadsHtmlRow
from vancelle.metadata import (
    JsonProperty,
    Details,
    IntoDetails,
    IntoProperties,
    IntoSource,
    CollectionProperty,
    Property,
    Source,
    UrlProperty,
)
from vancelle.types import WorkType, Shelf

T = TypeVar("T")


class Base(DeclarativeBase):
    pass


class User(Base, UserMixin):
    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()

    works: Mapped[List["Work"]] = relationship(
        back_populates="user",
        viewonly=True,
        lazy="dynamic",
    )

    def get_id(self) -> str:
        return str(self.id)


class Work(Base, IntoDetails):
    __tablename__ = "work"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User] = relationship(back_populates="works")

    id: Mapped[UUID] = mapped_column(primary_key=True)
    type: Mapped[WorkType] = mapped_column(String)

    time_created: Mapped[datetime] = mapped_column(default=func.now(), insert_default=func.now())
    time_updated: Mapped[Optional[datetime]] = mapped_column(default=None, onupdate=func.now())
    time_deleted: Mapped[Optional[datetime]] = mapped_column(default=None)

    title: Mapped[Optional[str]] = mapped_column(default=None)
    author: Mapped[Optional[str]] = mapped_column(default=None)
    description: Mapped[Optional[str]] = mapped_column(default=None)
    release_date: Mapped[Optional[date]] = mapped_column(default=None)
    cover: Mapped[Optional[str]] = mapped_column(default=None)
    background: Mapped[Optional[str]] = mapped_column(default=None)
    shelf: Mapped[Optional[Shelf]] = mapped_column(default=None)
    tags: Mapped[Optional[set[str]]] = mapped_column(ARRAY(String), default=None)

    records: Mapped[List["Record"]] = relationship(
        back_populates="work",
        order_by="Record.date_stopped, Record.date_started, Record.time_created",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    remotes: Mapped[List["Remote"]] = relationship(
        back_populates="work",
        order_by="Remote.id",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def deleted(self) -> bool:
        return self.time_deleted is not None

    def get_record(self) -> Optional["Record"]:
        return next((r for r in self.records if not r.deleted), None)

    @property
    def record(self) -> Optional["Record"]:
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

    def linkable_remotes(self) -> Mapping[str, Type["Remote"]]:
        present_remotes = {remote.type: remote for remote in self.remotes}
        absent_remotes = {
            remote_type: remote_cls
            for remote_type, remote_cls in Remote.classes().items()
            if remote_type not in present_remotes and remote_cls.into_source().can_link
        }
        return absent_remotes


class Record(Base):
    __tablename__ = "record"

    work_id: Mapped[UUID] = mapped_column(ForeignKey("work.id", ondelete="CASCADE"))
    id: Mapped[UUID] = mapped_column(primary_key=True)

    time_created: Mapped[datetime] = mapped_column(default=func.now(), insert_default=func.now())
    time_updated: Mapped[Optional[datetime]] = mapped_column(default=None, onupdate=func.now())
    time_deleted: Mapped[Optional[datetime]] = mapped_column(default=None)

    date_started: Mapped[Optional[date]] = mapped_column(default=None)
    date_stopped: Mapped[Optional[date]] = mapped_column(default=None)
    notes: Mapped[Optional[str]] = mapped_column(default=None)

    work: Mapped["Work"] = relationship(back_populates="records", lazy="raise")

    @property
    def deleted(self) -> bool:
        return self.time_deleted is not None

    def url_for(self) -> str:
        return url_for("records.detail", work_id=self.work_id, record_id=self.id)

    def entry_properties(self):
        yield Property("Started", self.date_started)
        yield Property("Stopped", self.date_stopped)


class Remote(Base, IntoSource, IntoDetails, IntoProperties):
    __tablename__ = "remote"
    __table__args = (UniqueConstraint("work_id", "type", name="work"),)
    __mapper_args__ = {"polymorphic_on": "type"}

    work_id: Mapped[UUID] = mapped_column(ForeignKey("work.id", ondelete="cascade"))
    type: Mapped[str] = mapped_column()

    time_created: Mapped[datetime] = mapped_column(default=func.now(), insert_default=func.now())
    time_updated: Mapped[Optional[datetime]] = mapped_column(default=None, onupdate=func.now())
    time_deleted: Mapped[Optional[datetime]] = mapped_column(default=None)

    id: Mapped[Optional[str]] = mapped_column(default=None, primary_key=True)
    title: Mapped[Optional[str]] = mapped_column(default=None)
    author: Mapped[Optional[str]] = mapped_column(default=None)
    description: Mapped[Optional[str]] = mapped_column(default=None)
    release_date: Mapped[Optional[date]] = mapped_column(default=None)
    cover: Mapped[Optional[str]] = mapped_column(default=None)
    background: Mapped[Optional[str]] = mapped_column(default=None)
    shelf: Mapped[Optional[Shelf]] = mapped_column(default=None)
    tags: Mapped[Optional[set[str]]] = mapped_column(ARRAY(String), default=None)
    data: Mapped[Optional[T]] = mapped_column(JSONB, default=None)

    work: Mapped["Work"] = relationship(back_populates="remotes", lazy="selectin")

    def url_for(self, work: "Work" = None) -> str:
        return url_for("remote.detail", remote_type=self.type, remote_id=self.id, work_id=work.id if work else None)

    @classmethod
    def into_source(cls) -> Source:
        raise NotImplementedError("Default remote type should not be instantiated")

    @property
    def deleted(self) -> bool:
        return self.time_deleted is not None

    def external_url(self) -> str | None:
        return None

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
            external_url=self.external_url(),
        )

    def into_properties(self) -> Iterable[Property]:
        yield Property("ID", self.id)
        yield UrlProperty("URL", self.external_url())

    def more_properties(self) -> Iterable[Property]:
        return []

    @classmethod
    def identity(cls) -> str:
        return cls.__mapper__.polymorphic_identity

    @classmethod
    def classes(cls) -> Mapping[str, Type["Remote"]]:
        return {remote_type: mapper.class_ for remote_type, mapper in cls.__mapper__.polymorphic_map.items()}

    @classmethod
    def sources(cls) -> Mapping[str, Source]:
        return {remote_type: mapper.class_.into_source() for remote_type, mapper in cls.__mapper__.polymorphic_map.items()}

    @classmethod
    def searchable_sources(cls) -> Mapping[str, Source]:
        return {remote_type: source for remote_type, source in cls.sources().items() if source.can_refresh}


class ImportedWorkAttributes(TypedDict):
    filename: str


class ImportedWork(Remote):
    __mapper_args__ = {"polymorphic_identity": "imported"}

    @classmethod
    def into_source(cls) -> Source:
        return Source(name="Imported", noun="work", priority=-1, can_search=False, can_link=False, can_refresh=False)

    def more_properties(self) -> Iterable[Property]:
        yield Property("Imported from", self.data.get("imported_from"))
        yield Property("Imported from path", self.data.get("filename"))
        yield Property("External URL", self.data.get("url"))


class GoodreadsBookData(TypedDict, GoodreadsCsvRow, GoodreadsHtmlRow):
    filename: str


class GoodreadsBook(Remote):
    __mapper_args__ = {"polymorphic_identity": "goodreads.book"}

    @classmethod
    def into_source(cls) -> Source:
        return Source(name="Goodreads", noun="book", work_type=WorkType.BOOK)

    def external_url(self) -> str | None:
        return f"https://www.goodreads.com/book/show/{self.id}"

    def into_properties(self) -> Iterable[Property]:
        yield from super().into_properties()
        yield Property(
            "Shelf",
            self.data.get("csv", {}).get("Exclusive Shelf", None)
            or self.data.get("html", {}).get("exclusive_shelf", None)
            or None,
        )

    def more_properties(self) -> Iterable[Property]:
        yield Property("ASIN", self.data.get("asin"))


class OpenlibraryWork(Remote):
    __mapper_args__ = {"polymorphic_identity": "openlibrary.work"}

    @classmethod
    def into_source(cls) -> Source:
        return Source(name="Open Library", noun="work", work_type=WorkType.BOOK, priority=1)

    def external_url(self) -> str:
        return f"https://openlibrary.org/works/{self.id}"

    def more_properties(self) -> Iterable[Property]:
        yield UrlProperty("API", self.data.get("url"))
        yield JsonProperty("Work", self.data.get("work"))


class OpenlibraryEdition(Remote):
    __mapper_args__ = {"polymorphic_identity": "openlibrary.edition"}

    @classmethod
    def into_source(cls) -> Source:
        return Source(name="Open Library", noun="edition", work_type=WorkType.BOOK, priority=2, can_search=False)

    def external_url(self) -> str:
        return f"https://openlibrary.org/books/{self.id}"

    def into_properties(self) -> Iterable[Property]:
        yield from super().into_properties()
        yield Property("ISBN", self.data.get("isbn13"))

    def more_properties(self) -> Iterable[Property]:
        yield UrlProperty("URL", self.external_url())
        yield UrlProperty("API", self.data.get("url"))
        yield JsonProperty("Edition", self.data.get("edition"))


class RoyalroadFiction(Remote):
    __mapper_args__ = {"polymorphic_identity": "royalroad.fiction"}

    def external_url(self) -> str:
        return f"https://www.royalroad.com/fiction/{self.id}"

    def into_properties(self) -> Iterable[Property]:
        yield UrlProperty("URL", self.external_url())

    @classmethod
    def into_source(cls) -> Source:
        return Source(name="Royal Road", noun="fiction", work_type=WorkType.BOOK, plural="fiction")


class SteamApplication(Remote):
    __mapper_args__ = {"polymorphic_identity": "steam.application"}

    @classmethod
    def into_source(cls) -> Source:
        return Source(name="Steam", noun="application", work_type=WorkType.GAME)

    def external_url(self) -> str | None:
        return f"https://store.steampowered.com/app/{self.id}/"

    def into_properties(self) -> Iterable[Property]:
        yield from super().into_properties()
        yield UrlProperty("Website", self.data.get("website"))
        yield CollectionProperty("Developers", [d for d in self.data.get("developers", []) if d])
        yield CollectionProperty("Publishers", [p for p in self.data.get("publishers", []) if p])

    def more_properties(self) -> Iterable[Property]:
        yield Property("Type", self.data.get("type"))
        yield UrlProperty("Background", self.data.get("background"))
        yield UrlProperty("Background (raw)", self.data.get("background_raw"))
        yield UrlProperty("Capsule image", self.data.get("capsule_image"))
        yield UrlProperty("Capsule image (v5)", self.data.get("capsule_imagev5"))
        yield UrlProperty("Header image", self.data.get("header_image"))


class TmdbMovie(Remote):
    __mapper_args__ = {"polymorphic_identity": "tmdb.movie"}

    @classmethod
    def into_source(cls) -> Source:
        return Source(name="TMDB", noun="movie", work_type=WorkType.FILM)


class TmdbTvSeries(Remote):
    __mapper_args__ = {"polymorphic_identity": "tmdb.tv"}

    @classmethod
    def into_source(cls) -> Source:
        return Source(name="TMDB", noun="series", work_type=WorkType.SHOW)
