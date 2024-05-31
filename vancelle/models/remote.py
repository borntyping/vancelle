import dataclasses
import datetime
import typing
import uuid

from flask import url_for
from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, PolymorphicBase
from .details import (
    Details,
    IntoDetails,
)
from .properties import ExternalUrlProperty, InternalUrlProperty, IntoProperties, IterableProperty, Property, StringProperty
from .types import ShelfEnum
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

    def plural(self, count: int) -> str:
        return self.noun if count == 1 else self.noun_plural

    def plural_full(self, count: int) -> str:
        return f"{self.source} {self.plural(count)}"

    @property
    def colour_invert(self) -> str:
        return f"{self.colour}-invert"


class Remote(PolymorphicBase, IntoDetails, IntoProperties):
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
    series: Mapped[typing.Optional[str]] = mapped_column(default=None)
    description: Mapped[typing.Optional[str]] = mapped_column(default=None)
    release_date: Mapped[typing.Optional[datetime.date]] = mapped_column(default=None)
    cover: Mapped[typing.Optional[str]] = mapped_column(default=None)
    background: Mapped[typing.Optional[str]] = mapped_column(default=None)
    tags: Mapped[typing.Optional[set[str]]] = mapped_column(ARRAY(String), default=None)
    data: Mapped[typing.Optional[typing.Any]] = mapped_column(JSONB, default=None)

    # The 'shelf' column is vestigial and can be removed. Check for data loss first.
    shelf: Mapped[typing.Optional[Shelf]] = mapped_column(ShelfEnum, default=None)

    work: Mapped["Work"] = relationship(back_populates="remotes", lazy="selectin")

    def url_for(self, work: typing.Optional["Work"] = None) -> str:
        return url_for("remote.detail", remote_type=self.type, remote_id=self.id, work_id=work.id if work else None)

    def url_for_cover(self) -> str | None:
        return url_for("remote.cover", remote_type=self.type, remote_id=self.id) if self.cover else None

    def url_for_background(self) -> str | None:
        return url_for("remote.background", remote_type=self.type, remote_id=self.id) if self.background else None

    @property
    def deleted(self) -> bool:
        return self.time_deleted is not None

    def external_url(self) -> str | None:
        return None

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
            external_url=self.external_url(),
        )

    def into_properties(self) -> typing.Iterable[Property]:
        yield StringProperty("ID", self.id)
        yield ExternalUrlProperty("Cover", self.cover)
        yield ExternalUrlProperty("Background", self.background)

    @classmethod
    def remote_type(cls) -> str:
        return cls.polymorphic_identity()

    @classmethod
    def filter_subclasses(cls, can_search: bool | None = None) -> typing.Sequence[typing.Type[typing.Self]]:
        subclasses = cls.iter_subclasses()
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
        colour="dark",
        source="Imported",
        noun="work",
        priority=-1,
        can_search=False,
        can_link=False,
        can_refresh=False,
    )

    def into_properties(self) -> typing.Iterable[StringProperty]:
        yield from super().into_properties()
        yield StringProperty("Imported from", self.data.get("imported_from"))
        yield StringProperty("Imported from path", self.data.get("filename"))
        yield StringProperty("External URL", self.data.get("url"))


class GoodreadsPrivateBook(Remote):
    """A Goodreads book imported from a CSV export or HTML dump of a user's books list."""

    __mapper_args__ = {"polymorphic_identity": "goodreads.book"}
    info = RemoteInfo(
        colour="dark",
        source="Goodreads",
        noun="book (imported)",
        noun_full="Goodreads book (imported)",
        noun_full_plural="Goodreads books (imported)",
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
        yield StringProperty("ASIN", self.data.get("asin"))


class GoodreadsPublicBook(Remote):
    """A Goodreads book scraped from the Goodreads website, without logging in."""

    __mapper_args__ = {"polymorphic_identity": "goodreads.book.public"}
    info = RemoteInfo(
        colour="success",
        source="Goodreads",
        noun="book",
        noun_full="Goodreads book",
        priority=13,
    )

    def external_url(self) -> str | None:
        return f"https://www.goodreads.com/book/show/{self.id}"

    def into_properties(self) -> typing.Iterable[StringProperty]:
        yield from super().into_properties()

        if data := self.data.get("data"):
            yield StringProperty("ISBN", data.get("isbn"))
            yield StringProperty("Number of pages", data.get("numberOfPages"))
            yield StringProperty("Name", data.get("name"))

        if scraped := self.data.get("scraped"):
            yield StringProperty("Series", scraped.get("series"))


class OpenlibraryWork(Remote):
    __mapper_args__ = {"polymorphic_identity": "openlibrary.work"}
    info = RemoteInfo(
        colour="success",
        source="Open Library",
        noun="work",
        priority=11,
    )

    def external_url(self) -> str:
        return f"https://openlibrary.org/works/{self.id}"


class OpenlibraryEdition(Remote):
    __mapper_args__ = {"polymorphic_identity": "openlibrary.edition"}
    info = RemoteInfo(
        colour="success",
        source="Open Library",
        noun="edition",
        priority=12,
        can_search=False,
    )

    def external_url(self) -> str:
        return f"https://openlibrary.org/books/{self.id}"

    def into_properties(self) -> typing.Iterable[StringProperty]:
        yield from super().into_properties()
        yield StringProperty("ISBN", self.data.get("isbn13"))
        yield ExternalUrlProperty("URL", self.external_url())
        yield ExternalUrlProperty("API", self.data.get("url"))


class RoyalroadFiction(Remote):
    __mapper_args__ = {"polymorphic_identity": "royalroad.fiction"}
    info = RemoteInfo(
        colour="success",
        source="Royal Road",
        noun="fiction",
        noun_plural="fictions",
        priority=20,
    )

    def external_url(self) -> str:
        return f"https://www.royalroad.com/fiction/{self.id}"


class SteamApplication(Remote):
    __mapper_args__ = {"polymorphic_identity": "steam.application"}
    info = RemoteInfo(
        colour="danger",
        source="Steam",
        noun="app",
        priority=99,
    )

    def external_url(self) -> str | None:
        return f"https://store.steampowered.com/app/{self.id}/"

    def into_properties(self) -> typing.Iterable[Property]:
        yield from super().into_properties()
        yield ExternalUrlProperty("Website", self.data.get("website"))

        if fullgame := self.data.get("fullgame"):
            url = url_for("remote.detail", remote_type=self.remote_type(), remote_id=fullgame["appid"])
            yield InternalUrlProperty("Full game", url, fullgame["name"])

        if dlc := self.data.get("dlc"):
            for appid in dlc:
                url = url_for("remote.detail", remote_type=self.remote_type(), remote_id=appid)
                yield InternalUrlProperty("DLC", url, str(appid))

        yield IterableProperty("Developers", [d for d in self.data.get("developers", []) if d])
        yield IterableProperty("Publishers", [p for p in self.data.get("publishers", []) if p])

        yield StringProperty("Type", self.data.get("type"))
        yield ExternalUrlProperty("Background", self.data.get("background"))
        yield ExternalUrlProperty("Background (raw)", self.data.get("background_raw"))
        yield ExternalUrlProperty("Capsule image", self.data.get("capsule_image"))
        yield ExternalUrlProperty("Capsule image (v5)", self.data.get("capsule_imagev5"))
        yield ExternalUrlProperty("Header image", self.data.get("header_image"))


class TmdbMovie(Remote):
    __mapper_args__ = {"polymorphic_identity": "tmdb.movie"}
    info = RemoteInfo(
        colour="info",
        source="TMDB",
        noun="movie",
        priority=40,
    )

    def external_url(self) -> str | None:
        return f"https://www.themoviedb.org/movie/{self.id}"


class TmdbTvSeries(Remote):
    __mapper_args__ = {"polymorphic_identity": "tmdb.tv"}
    info = RemoteInfo(
        colour="info",
        source="TMDB",
        noun="series",
        priority=31,
    )

    def external_url(self) -> str | None:
        return f"https://www.themoviedb.org/tv/{self.id}"
