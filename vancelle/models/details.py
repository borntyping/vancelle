import dataclasses
import datetime
import typing
import urllib.parse

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


@dataclasses.dataclass()
class StringProperty(Property):
    name: str
    value: str | typing.Any

    def __bool__(self) -> bool:
        return bool(self.value)

    def __str__(self) -> str:
        return str(self.value) if self else self.absent()


@dataclasses.dataclass()
class UrlProperty(Property):
    name: str
    link: str | None
    text: str | None = None

    def __bool__(self) -> bool:
        return bool(self.link or self.text)

    def __str__(self) -> str:
        if not self:
            return self.absent()

        text = self.text or urllib.parse.urlparse(self.link).hostname
        external_link = flask.get_template_attribute("components/links.html", "external_link")
        return external_link(href=self.link, text=text)


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
        render = flask.get_template_attribute("components/metadata.html", "list_property")
        return render(property=self)


@dataclasses.dataclass()
class JsonProperty(Property):
    name: str
    value: typing.Any

    def __bool__(self) -> bool:
        return bool(self.value)

    def __html__(self) -> str:
        if not self:
            return self.absent()

        if isinstance(self.value, dict):
            return flask.render_template_string("<pre><code>{{ value|tojson(indent=2) }}</code></pre>", value=self.value)

        return flask.render_template_string("<code>{{ value }}</code>", value=self.value)


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

    def more_properties(self) -> typing.Iterable[Property]:
        yield UrlProperty("Cover", self.cover)
        yield UrlProperty("Background", self.background)


class IntoDetails:
    def into_details(self) -> Details:
        raise NotImplementedError()
