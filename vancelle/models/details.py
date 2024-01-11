import dataclasses
import datetime
import typing

import flask
import structlog

from vancelle.shelf import Shelf

logger = structlog.get_logger(logger_name=__name__)


class Property:
    name: str

    def __bool__(self) -> bool:
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError

    def absent(self) -> str:
        return flask.render_template_string("{{ absent }}")

    @staticmethod
    def macro(attribute: str, **context: typing.Any) -> str:
        render = flask.get_template_attribute("components/metadata.html", attribute)
        return render(**context)


@dataclasses.dataclass()
class StringProperty(Property):
    name: str
    value: str | typing.Any

    def __bool__(self) -> bool:
        return bool(self.value)

    def __str__(self) -> str:
        return str(self.value) if self else self.absent()


@dataclasses.dataclass()
class TimeProperty(Property):
    name: str
    value: datetime.datetime | datetime.date | typing.Any

    def __bool__(self) -> bool:
        return self.value is not None

    def __str__(self) -> str:
        return self.macro("time_property", property=self)


@dataclasses.dataclass()
class InternalUrlProperty(Property):
    name: str
    link: str | None
    text: str | None = None

    def __bool__(self) -> bool:
        return bool(self.link or self.text)

    def __str__(self) -> str:
        if not self:
            return self.absent()

        return self.macro("internal_link", href=self.link, text=self.text)


@dataclasses.dataclass()
class ExternalUrlProperty(Property):
    name: str
    link: str | None
    text: str | None = None

    def __bool__(self) -> bool:
        return bool(self.link or self.text)

    def __str__(self) -> str:
        if not self:
            return self.absent()

        return self.macro("external_link", href=self.link, text=self.text)


@dataclasses.dataclass()
class IterableProperty(Property):
    name: str
    items: typing.Iterable[typing.Any] = ()
    sorted: bool = False

    def __bool__(self) -> bool:
        return bool(self.items)

    def __iter__(self):
        return sorted(self.items) if self.sorted else iter(self.items)

    def __str__(self) -> str:
        return self.macro("list_property", property=self)


class IntoProperties:
    def into_properties(self) -> typing.Iterable[Property]:
        return ()

    def more_properties(self) -> typing.Iterable[Property]:
        return ()


@dataclasses.dataclass(kw_only=True)
class Details(IntoProperties):
    """Details describe static information about a work."""

    title: str | None
    author: str | None
    description: str | None
    release_date: datetime.date | None
    cover: str | None
    background: str | None
    shelf: Shelf | None
    tags: typing.Set[str] | None = dataclasses.field(default_factory=set)
    external_url: str | None

    def __str__(self) -> str:
        d = f"{self.title}"

        if self.author:
            d += f", {self.author}"

        if self.release_date:
            d += f" ({self.release_date.year})"

        return d

    def into_properties(self) -> typing.Iterable[Property]:
        yield StringProperty("Title", self.title)
        yield StringProperty("Author", self.author)
        yield StringProperty("Release date", self.release_date)
        yield StringProperty("Shelf", self.shelf.title if self.shelf else None)
        yield IterableProperty("Tags", list(self.tags) if self.tags else ())
        yield ExternalUrlProperty("External URL", self.external_url)
        yield ExternalUrlProperty("Cover URL", self.cover)
        yield ExternalUrlProperty("Background URL", self.background)


class IntoDetails:
    def into_details(self) -> Details:
        raise NotImplementedError()
