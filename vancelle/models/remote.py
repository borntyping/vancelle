import dataclasses
import datetime
import typing
import uuid

from flask import url_for
from sqlalchemy import Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .details import (
    CollectionProperty,
    Details,
    IntoDetails,
    IntoProperties,
    JsonProperty,
    Property,
    UrlProperty,
)
from ..clients.goodreads.types import GoodreadsCsvRow, GoodreadsHtmlRow
from ..inflect import p
from ..types import Shelf

if typing.TYPE_CHECKING:
    from .work import Work

T = typing.TypeVar("T")


@dataclasses.dataclass(kw_only=True)
class RemoteInfo:
    name: str
    noun: str
    plural: str = None

    priority: int = 0

    can_search: bool = True
    can_link: bool = True
    can_refresh: bool = True

    def __init__(
        self,
        name: str,
        noun: str,
        *,
        plural: str = None,
        priority: int = 0,
        can_search: bool = True,
        can_link: bool = True,
        can_refresh: bool = True,
    ) -> None:
        self.name = name
        self.noun = noun
        self.plural = plural if plural is not None else p.plural(noun)
        self.priority = priority
        self.can_search = can_search
        self.can_link = can_link
        self.can_refresh = can_refresh

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        return self.full_noun

    @property
    def full_noun(self) -> str:
        return f"{self.name} {self.noun}"

    @property
    def full_plural(self) -> str:
        return f"{self.name} {self.plural or p.plural(self.noun)}"


class Remote(Base, IntoDetails, IntoProperties):
    __tablename__ = "remote"
    __mapper_args__ = {"polymorphic_on": "type"}

    info: typing.ClassVar[RemoteInfo]

    work_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("work.id", ondelete="cascade"))
    type: Mapped[str] = mapped_column(primary_key=True)

    time_created: Mapped[datetime.datetime] = mapped_column(default=func.now(), insert_default=func.now())
    time_updated: Mapped[typing.Optional[datetime.datetime]] = mapped_column(default=None, onupdate=func.now())
    time_deleted: Mapped[typing.Optional[datetime.datetime]] = mapped_column(default=None)

    id: Mapped[typing.Optional[str]] = mapped_column(default=None, primary_key=True)
    title: Mapped[typing.Optional[str]] = mapped_column(default=None)
    author: Mapped[typing.Optional[str]] = mapped_column(default=None)
    description: Mapped[typing.Optional[str]] = mapped_column(default=None)
    release_date: Mapped[typing.Optional[datetime.date]] = mapped_column(default=None)
    cover: Mapped[typing.Optional[str]] = mapped_column(default=None)
    background: Mapped[typing.Optional[str]] = mapped_column(default=None)
    shelf: Mapped[typing.Optional[Shelf]] = mapped_column(Enum(Shelf, native_enum=False, validate_strings=True), default=None)
    tags: Mapped[typing.Optional[set[str]]] = mapped_column(ARRAY(String), default=None)
    data: Mapped[typing.Optional[T]] = mapped_column(JSONB, default=None)

    work: Mapped["Work"] = relationship(back_populates="remotes", lazy="selectin")

    def url_for(self, work: "Work" = None) -> str:
        return url_for("remote.detail", remote_type=self.type, remote_id=self.id, work_id=work.id if work else None)

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

    def into_properties(self) -> typing.Iterable[Property]:
        yield Property("ID", self.id)
        yield UrlProperty("URL", self.external_url())

    def more_properties(self) -> typing.Iterable[Property]:
        return []

    @classmethod
    def identity(cls) -> str:
        return cls.__mapper__.polymorphic_identity

    @classmethod
    def subclasses(cls) -> typing.Mapping[str, typing.Type["Remote"]]:
        return {remote_type: mapper.class_ for remote_type, mapper in cls.__mapper__.polymorphic_map.items()}

    @classmethod
    def sources(cls) -> typing.Mapping[str, RemoteInfo]:
        return {remote_type: mapper.class_.info for remote_type, mapper in cls.__mapper__.polymorphic_map.items()}

    @classmethod
    def searchable_sources(cls) -> typing.Mapping[str, RemoteInfo]:
        return {remote_type: source for remote_type, source in cls.sources().items() if source.can_refresh}


class ImportedWorkAttributes(typing.TypedDict):
    filename: str


class ImportedWork(Remote):
    __mapper_args__ = {"polymorphic_identity": "imported"}

    info = RemoteInfo(name="Imported", noun="work", priority=-1, can_search=False, can_link=False, can_refresh=False)

    def more_properties(self) -> typing.Iterable[Property]:
        yield Property("Imported from", self.data.get("imported_from"))
        yield Property("Imported from path", self.data.get("filename"))
        yield Property("External URL", self.data.get("url"))


class GoodreadsBookData(typing.TypedDict, GoodreadsCsvRow, GoodreadsHtmlRow):
    filename: str


class GoodreadsBook(Remote):
    __mapper_args__ = {"polymorphic_identity": "goodreads.book"}
    info = RemoteInfo(name="Goodreads", noun="book")

    def external_url(self) -> str | None:
        return f"https://www.goodreads.com/book/show/{self.id}"

    def into_properties(self) -> typing.Iterable[Property]:
        yield from super().into_properties()
        yield Property(
            "Shelf",
            self.data.get("csv", {}).get("Exclusive Shelf", None)
            or self.data.get("html", {}).get("exclusive_shelf", None)
            or None,
        )

    def more_properties(self) -> typing.Iterable[Property]:
        yield Property("ASIN", self.data.get("asin"))


class OpenlibraryWork(Remote):
    __mapper_args__ = {"polymorphic_identity": "openlibrary.work"}
    info = RemoteInfo(name="Open Library", noun="work", priority=1)

    def external_url(self) -> str:
        return f"https://openlibrary.org/works/{self.id}"

    def more_properties(self) -> typing.Iterable[Property]:
        yield UrlProperty("API", self.data.get("url"))
        yield JsonProperty("Work", self.data.get("work"))


class OpenlibraryEdition(Remote):
    __mapper_args__ = {"polymorphic_identity": "openlibrary.edition"}
    info = RemoteInfo(name="Open Library", noun="edition", priority=2, can_search=False)

    def external_url(self) -> str:
        return f"https://openlibrary.org/books/{self.id}"

    def into_properties(self) -> typing.Iterable[Property]:
        yield from super().into_properties()
        yield Property("ISBN", self.data.get("isbn13"))

    def more_properties(self) -> typing.Iterable[Property]:
        yield UrlProperty("URL", self.external_url())
        yield UrlProperty("API", self.data.get("url"))
        yield JsonProperty("Edition", self.data.get("edition"))


class RoyalroadFiction(Remote):
    __mapper_args__ = {"polymorphic_identity": "royalroad.fiction"}
    info = RemoteInfo(name="Royal Road", noun="fiction", plural="fiction")

    def external_url(self) -> str:
        return f"https://www.royalroad.com/fiction/{self.id}"

    def into_properties(self) -> typing.Iterable[Property]:
        yield UrlProperty("URL", self.external_url())


class SteamApplication(Remote):
    __mapper_args__ = {"polymorphic_identity": "steam.application"}
    info = RemoteInfo(name="Steam", noun="application")

    def external_url(self) -> str | None:
        return f"https://store.steampowered.com/app/{self.id}/"

    def into_properties(self) -> typing.Iterable[Property]:
        yield from super().into_properties()
        yield UrlProperty("Website", self.data.get("website"))
        yield CollectionProperty("Developers", [d for d in self.data.get("developers", []) if d])
        yield CollectionProperty("Publishers", [p for p in self.data.get("publishers", []) if p])

    def more_properties(self) -> typing.Iterable[Property]:
        yield Property("Type", self.data.get("type"))
        yield UrlProperty("Background", self.data.get("background"))
        yield UrlProperty("Background (raw)", self.data.get("background_raw"))
        yield UrlProperty("Capsule image", self.data.get("capsule_image"))
        yield UrlProperty("Capsule image (v5)", self.data.get("capsule_imagev5"))
        yield UrlProperty("Header image", self.data.get("header_image"))


class TmdbMovie(Remote):
    __mapper_args__ = {"polymorphic_identity": "tmdb.movie"}
    info = RemoteInfo(name="TMDB", noun="movie")


class TmdbTvSeries(Remote):
    __mapper_args__ = {"polymorphic_identity": "tmdb.tv"}
    info = RemoteInfo(name="TMDB", noun="series")
