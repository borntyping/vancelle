import dataclasses
import datetime
import typing
import uuid

from flask import url_for
from sqlalchemy import Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .details import (
    Property,
    IterableProperty,
    Details,
    IntoDetails,
    IntoProperties,
    JsonProperty,
    StringProperty,
    UrlProperty,
)
from .types import ShelfEnum
from ..clients.goodreads.types import GoodreadsCsvRow, GoodreadsHtmlRow
from ..clients.steam.client_store_api import AppDetails
from ..inflect import p
from ..shelf import Shelf

if typing.TYPE_CHECKING:
    from .work import Work

T = typing.TypeVar("T")


@dataclasses.dataclass(kw_only=True)
class RemoteInfo:
    source: str  # Name of the source these remotes come from
    noun: str  # Noun for this type of remote
    noun_plural: str
    noun_full: str  # Source and noun combined

    colour: str  # Used in CSS
    priority: int = 0

    can_search: bool = True
    can_link: bool = True
    can_refresh: bool = True

    def __init__(
        self,
        source: str,
        noun: str,
        *,
        colour: str,
        noun_plural: str | None = None,
        noun_full: str | None = None,
        noun_full_plural: str | None = None,
        priority: int = 0,
        can_search: bool = True,
        can_link: bool = True,
        can_refresh: bool = True,
    ) -> None:
        self.colour = colour
        self.source = source
        self.noun = noun
        self.noun_plural = noun_plural if noun_plural is not None else p.plural(noun)
        self.noun_full = noun_full or f"{self.source} {self.noun}"
        self.noun_full_plural = noun_full_plural or f"{self.source} {self.noun_plural}"
        self.priority = priority
        self.can_search = can_search
        self.can_link = can_link
        self.can_refresh = can_refresh

    def __str__(self) -> str:
        return self.noun_full

    @property
    def full_plural(self) -> str:
        return f"{self.source} {self.noun_plural or p.plural(self.noun)}"


class Remote(Base, IntoDetails, IntoProperties):
    __tablename__ = "remote"
    __mapper_args__ = {"polymorphic_on": "type"}

    info: typing.ClassVar[RemoteInfo]

    work_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("work.id", ondelete="cascade"))
    type: Mapped[str] = mapped_column(primary_key=True)

    time_created: Mapped[datetime.datetime] = mapped_column(default=func.now(), insert_default=func.now())
    time_updated: Mapped[typing.Optional[datetime.datetime]] = mapped_column(default=None, onupdate=func.now())
    time_deleted: Mapped[typing.Optional[datetime.datetime]] = mapped_column(default=None)

    id: Mapped[str] = mapped_column(Text(collation="numeric"), default=None, primary_key=True)
    title: Mapped[typing.Optional[str]] = mapped_column(default=None)
    author: Mapped[typing.Optional[str]] = mapped_column(default=None)
    description: Mapped[typing.Optional[str]] = mapped_column(default=None)
    release_date: Mapped[typing.Optional[datetime.date]] = mapped_column(default=None)
    cover: Mapped[typing.Optional[str]] = mapped_column(default=None)
    background: Mapped[typing.Optional[str]] = mapped_column(default=None)
    shelf: Mapped[typing.Optional[Shelf]] = mapped_column(ShelfEnum, default=None)
    tags: Mapped[typing.Optional[set[str]]] = mapped_column(ARRAY(String), default=None)
    data: Mapped[typing.Optional[typing.Any]] = mapped_column(JSONB, default=None)

    work: Mapped["Work"] = relationship(back_populates="remotes", lazy="selectin")

    def url_for(self, work: typing.Optional["Work"] = None) -> str:
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
        yield UrlProperty(self.info.source, self.external_url())

    def more_properties(self) -> typing.Iterable[Property]:
        yield StringProperty("ID", self.id)

    @classmethod
    def remote_type(cls) -> str:
        assert cls.__mapper__.polymorphic_identity is not None
        return cls.__mapper__.polymorphic_identity

    @classmethod
    def subclasses(cls) -> typing.Mapping[str, typing.Type["Remote"]]:
        return {remote_type: mapper.class_ for remote_type, mapper in cls.__mapper__.polymorphic_map.items()}

    @classmethod
    def iter_subclasses(cls, can_search: bool | None = None) -> typing.Sequence[typing.Type["Remote"]]:
        subclasses = (subclass.class_ for subclass in cls.__mapper__.polymorphic_map.values())
        subclasses = sorted(subclasses, key=lambda subclass: subclass.info.priority, reverse=True)

        if can_search is not None:
            subclasses = (s for s in subclasses if s.info.can_search)

        return list(subclasses)

    @classmethod
    def iter_subclasses_for_search(cls) -> typing.Sequence[typing.Type["Remote"]]:
        return [subclass for subclass in cls.iter_subclasses() if subclass.info.can_search]


class ImportedWorkAttributes(typing.TypedDict):
    filename: str


class ImportedWork(Remote):
    __mapper_args__ = {"polymorphic_identity": "imported"}
    info = RemoteInfo(
        colour="imported",
        source="Imported",
        noun="work",
        priority=-1,
        can_search=False,
        can_link=False,
        can_refresh=False,
    )

    def more_properties(self) -> typing.Iterable[StringProperty]:
        yield StringProperty("Imported from", self.data.get("imported_from"))
        yield StringProperty("Imported from path", self.data.get("filename"))
        yield StringProperty("External URL", self.data.get("url"))


class GoodreadsBookData(typing.TypedDict, GoodreadsCsvRow, GoodreadsHtmlRow):
    filename: str


class GoodreadsBook(Remote):
    __mapper_args__ = {"polymorphic_identity": "goodreads.book"}
    info = RemoteInfo(
        colour="goodreads",
        source="Goodreads",
        noun="book",
        noun_full="Imported Goodreads book",
        priority=10,
        can_search=False,
    )

    def external_url(self) -> str | None:
        return f"https://www.goodreads.com/book/show/{self.id}"

    def into_properties(self) -> typing.Iterable[StringProperty]:
        yield from super().into_properties()
        yield StringProperty(
            "Shelf",
            self.data.get("csv", {}).get("Exclusive Shelf", None)
            or self.data.get("html", {}).get("exclusive_shelf", None)
            or None,
        )

    def more_properties(self) -> typing.Iterable[StringProperty]:
        yield StringProperty("ASIN", self.data.get("asin"))


class OpenlibraryWork(Remote):
    __mapper_args__ = {"polymorphic_identity": "openlibrary.work"}
    info = RemoteInfo(
        colour="openlibrary",
        source="Open Library",
        noun="work",
        priority=21,
    )

    def external_url(self) -> str:
        return f"https://openlibrary.org/works/{self.id}"

    def more_properties(self) -> typing.Iterable[StringProperty]:
        yield UrlProperty("API", self.data.get("url"))
        yield JsonProperty("Work", self.data.get("work"))


class OpenlibraryEdition(Remote):
    __mapper_args__ = {"polymorphic_identity": "openlibrary.edition"}
    info = RemoteInfo(
        colour="openlibrary",
        source="Open Library",
        noun="edition",
        priority=22,
        can_search=False,
    )

    def external_url(self) -> str:
        return f"https://openlibrary.org/books/{self.id}"

    def into_properties(self) -> typing.Iterable[StringProperty]:
        yield from super().into_properties()
        yield StringProperty("ISBN", self.data.get("isbn13"))

    def more_properties(self) -> typing.Iterable[StringProperty]:
        yield UrlProperty("URL", self.external_url())
        yield UrlProperty("API", self.data.get("url"))
        yield JsonProperty("Edition", self.data.get("edition"))


class RoyalroadFiction(Remote):
    __mapper_args__ = {"polymorphic_identity": "royalroad.fiction"}
    info = RemoteInfo(
        colour="royalroad",
        source="Royal Road",
        noun="fiction",
        noun_plural="fiction",
        priority=20,
    )

    def external_url(self) -> str:
        return f"https://www.royalroad.com/fiction/{self.id}"


class SteamApplication(Remote):
    __mapper_args__ = {"polymorphic_identity": "steam.application"}
    info = RemoteInfo(
        colour="steam",
        source="Steam",
        noun="application",
        priority=100,
    )

    def external_url(self) -> str | None:
        return f"https://store.steampowered.com/app/{self.id}/"

    def into_properties(self) -> typing.Iterable[Property]:
        yield from super().into_properties()
        yield UrlProperty("Website", self.data.get("website"))

        if fullgame := self.data.get("fullgame"):
            url = url_for("remote.detail", remote_type=self.remote_type(), remote_id=fullgame["appid"])
            yield UrlProperty("Full game", url, fullgame["name"], external=False)

        if dlc := self.data.get("dlc"):
            for appid in dlc:
                url = url_for("remote.detail", remote_type=self.remote_type(), remote_id=appid)
                yield UrlProperty("DLC", url, appid, external=False)

        yield IterableProperty("Developers", [d for d in self.data.get("developers", []) if d])
        yield IterableProperty("Publishers", [p for p in self.data.get("publishers", []) if p])

    def more_properties(self) -> typing.Iterable[Property]:
        yield StringProperty("Type", self.data.get("type"))
        yield UrlProperty("Background", self.data.get("background"))
        yield UrlProperty("Background (raw)", self.data.get("background_raw"))
        yield UrlProperty("Capsule image", self.data.get("capsule_image"))
        yield UrlProperty("Capsule image (v5)", self.data.get("capsule_imagev5"))
        yield UrlProperty("Header image", self.data.get("header_image"))


class TmdbMovie(Remote):
    __mapper_args__ = {"polymorphic_identity": "tmdb.movie"}
    info = RemoteInfo(
        colour="tmdb-movie",
        source="TMDB",
        noun="movie",
        priority=40,
    )

    def external_url(self) -> str | None:
        return f"https://www.themoviedb.org/movie/{self.id}"


class TmdbTvSeries(Remote):
    __mapper_args__ = {"polymorphic_identity": "tmdb.tv"}
    info = RemoteInfo(
        colour="tmdb-tv",
        source="TMDB",
        noun="series",
        priority=31,
    )

    def external_url(self) -> str | None:
        return f"https://www.themoviedb.org/tv/{self.id}"
