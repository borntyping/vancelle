import dataclasses
import datetime
import typing
import uuid

import flask
from flask import url_for
from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import PolymorphicBase
from .details import Details, IntoDetails
from .properties import (
    CodeProperty,
    ExternalUrlProperty,
    InternalUrlProperty,
    IntoProperties,
    IterableProperty,
    Property,
    StringProperty,
)
from .types import ShelfEnum
from ..html.bootstrap.variables import ThemeColor
from ..inflect import p
from ..shelf import Shelf

if typing.TYPE_CHECKING:
    from .work import Work

T = typing.TypeVar("T")


@dataclasses.dataclass(kw_only=True)
class EntryInfo(IntoProperties):
    origin: str  # 'imported'
    noun: str  # 'book'
    noun_plural: str  # 'books'
    noun_full: str  # 'imported book'

    priority: int = 0
    colour: ThemeColor  # Used in CSS

    is_external_source: bool = True

    def __init__(
        self,
        origin: str,
        noun: str,
        *,
        colour: ThemeColor,
        noun_plural: str | None = None,
        noun_full: str | None = None,
        noun_full_plural: str | None = None,
        priority: int = 0,
        is_external_source: bool = True,
    ) -> None:
        self.colour = colour
        self.origin = origin
        self.noun = noun
        self.noun_plural = noun_plural if noun_plural is not None else p.plural(noun)
        self.noun_full = noun_full or f"{self.origin} {self.noun}"
        self.noun_full_plural = noun_full_plural or f"{self.origin} {self.noun_plural}"
        self.priority = priority
        self.is_external_source = is_external_source

    def __str__(self) -> str:
        return self.noun_full

    def plural(self, count: int) -> str:
        return self.noun if count == 1 else self.noun_plural

    def plural_full(self, count: int) -> str:
        return f"{self.origin} {self.plural(count)}"

    def into_properties(self) -> typing.Iterable[Property]:
        yield StringProperty("Name", self.noun_full, title="Entry type.")
        yield StringProperty("Priority", self.priority, title="Priority for this entry type.")


class Entry(PolymorphicBase, IntoDetails, IntoProperties):
    """
    An entry in our catalogue.

    Works are made up of multiple entries.

    An entry *may* represent remote data from an external source.
    """

    __tablename__ = "remote"
    __mapper_args__ = {"polymorphic_on": "type"}

    info: typing.ClassVar[EntryInfo]

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

    work: Mapped["Work"] = relationship(back_populates="entries", lazy="selectin")

    def url_for(self) -> str:
        return url_for("entry.detail", entry_type=self.type, entry_id=self.id)

    def url_for_cover(self) -> str | None:
        return url_for("entry.cover", entry_type=self.type, entry_id=self.id) if self.cover else None

    def url_for_background(self) -> str | None:
        return url_for("entry.background", entry_type=self.type, entry_id=self.id) if self.background else None

    def url_for_index(self) -> str:
        return flask.url_for("entry.index", entry_type=self.type)

    def url_for_delete(self) -> str:
        return flask.url_for("entry.delete", entry_type=self.type, entry_id=self.id)

    def url_for_restore(self) -> str:
        return flask.url_for("entry.restore", entry_type=self.type, entry_id=self.id)

    def url_for_permanently_delete(self) -> str:
        return flask.url_for("entry.permanently_delete", entry_type=self.type, entry_id=self.id)

    def url_for_refresh(self) -> str:
        assert self.info.is_external_source, "Entry type is not an external source"
        return flask.url_for("source.refresh", entry_type=self.type, entry_id=self.id)

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
        yield CodeProperty("ID", self.id, title="Unique ID for this entry.")
        yield ExternalUrlProperty("Cover", self.cover)
        yield ExternalUrlProperty("Background", self.background)

    def resolve_title(self) -> str:
        return self.title if self.title else self.resolve_subtitle()

    def resolve_subtitle(self) -> str:
        return f"{self.info.noun_full} {self.id}"


class ImportedWorkAttributes(typing.TypedDict):
    filename: str


class ImportedWork(Entry):
    __mapper_args__ = {"polymorphic_identity": "imported"}
    info = EntryInfo(
        colour="dark",
        origin="Imported",
        noun="work",
        priority=-1,
        is_external_source=False,
    )

    def into_properties(self) -> typing.Iterable[Property]:
        yield from super().into_properties()
        yield CodeProperty("Filename", self.data.get("filename"))
        yield StringProperty("External URL", self.data.get("url"))


class GoodreadsPrivateBook(Entry):
    """A Goodreads book imported from a CSV export or HTML dump of a user's books list."""

    __mapper_args__ = {"polymorphic_identity": "goodreads.book"}
    info = EntryInfo(
        colour="dark",
        origin="Goodreads",
        noun="book (imported)",
        noun_full="Goodreads book (imported)",
        noun_full_plural="Goodreads books (imported)",
        priority=10,
        is_external_source=False,
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


class GoodreadsPublicBook(Entry):
    """A Goodreads book scraped from the Goodreads website, without logging in."""

    __mapper_args__ = {"polymorphic_identity": "goodreads.book.public"}
    info = EntryInfo(
        colour="success",
        origin="Goodreads",
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


class OpenlibraryWork(Entry):
    __mapper_args__ = {"polymorphic_identity": "openlibrary.work"}
    info = EntryInfo(
        colour="success",
        origin="Open Library",
        noun="work",
        priority=11,
    )

    def external_url(self) -> str:
        return f"https://openlibrary.org/works/{self.id}"


class OpenlibraryEdition(Entry):
    __mapper_args__ = {"polymorphic_identity": "openlibrary.edition"}
    info = EntryInfo(
        colour="success",
        origin="Open Library",
        noun="edition",
        priority=12,
        is_external_source=False,
    )

    def external_url(self) -> str:
        return f"https://openlibrary.org/books/{self.id}"

    def into_properties(self) -> typing.Iterable[StringProperty]:
        yield from super().into_properties()
        yield StringProperty("ISBN", self.data.get("isbn13"))
        yield ExternalUrlProperty("URL", self.external_url())
        yield ExternalUrlProperty("API", self.data.get("url"))


class RoyalroadFiction(Entry):
    __mapper_args__ = {"polymorphic_identity": "royalroad.fiction"}
    info = EntryInfo(
        colour="success",
        origin="Royal Road",
        noun="fiction",
        noun_plural="fictions",
        priority=20,
    )

    def external_url(self) -> str:
        return f"https://www.royalroad.com/fiction/{self.id}"


class SteamApplication(Entry):
    __mapper_args__ = {"polymorphic_identity": "steam.application"}
    info = EntryInfo(
        colour="danger",
        origin="Steam",
        noun="app",
        priority=99,
    )

    def external_url(self) -> str | None:
        return f"https://store.steampowered.com/app/{self.id}/"

    def into_properties(self) -> typing.Iterable[Property]:
        yield from super().into_properties()
        yield ExternalUrlProperty("Website", self.data.get("website"))

        if fullgame := self.data.get("fullgame"):
            url = url_for("entry.detail", entry_type=self.type, entry_id=fullgame["appid"])
            yield InternalUrlProperty("Full game", url, fullgame["name"])

        if dlc := self.data.get("dlc"):
            for appid in dlc:
                url = url_for("entry.detail", entry_type=self.type, entry_id=appid)
                yield InternalUrlProperty("DLC", url, str(appid))

        yield IterableProperty("Developers", [d for d in self.data.get("developers", []) if d])
        yield IterableProperty("Publishers", [p for p in self.data.get("publishers", []) if p])

        yield StringProperty("Type", self.data.get("type"))
        yield ExternalUrlProperty("Background", self.data.get("background"))
        yield ExternalUrlProperty("Background (raw)", self.data.get("background_raw"))
        yield ExternalUrlProperty("Capsule image", self.data.get("capsule_image"))
        yield ExternalUrlProperty("Capsule image (v5)", self.data.get("capsule_imagev5"))
        yield ExternalUrlProperty("Header image", self.data.get("header_image"))


class TmdbMovie(Entry):
    __mapper_args__ = {"polymorphic_identity": "tmdb.movie"}
    info = EntryInfo(
        colour="info",
        origin="TMDB",
        noun="movie",
        priority=40,
    )

    def external_url(self) -> str | None:
        return f"https://www.themoviedb.org/movie/{self.id}"


class TmdbTvSeries(Entry):
    __mapper_args__ = {"polymorphic_identity": "tmdb.tv"}
    info = EntryInfo(
        colour="info",
        origin="TMDB",
        noun="series",
        priority=31,
    )

    def external_url(self) -> str | None:
        return f"https://www.themoviedb.org/tv/{self.id}"
