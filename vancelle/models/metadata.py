import dataclasses
import datetime
import typing
import urllib.parse

import flask
import structlog

from vancelle.inflect import p
from vancelle.types import Shelf

logger = structlog.get_logger(logger_name=__name__)


class BaseProperty:
    name: str

    def __bool__(self) -> bool:
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError

    def absent(self) -> str:
        return flask.render_template_string("{{ absent }}")


@dataclasses.dataclass()
class Property(BaseProperty):
    name: str
    value: str | typing.Any

    def __bool__(self) -> bool:
        return bool(self.value)

    def __str__(self) -> str:
        return str(self.value) if self else self.absent()


@dataclasses.dataclass()
class UrlProperty(BaseProperty):
    name: str
    link: str = None
    text: str = None

    def __bool__(self) -> bool:
        return bool(self.link or self.text)

    def __str__(self) -> str:
        if not self:
            return self.absent()

        text = self.text or urllib.parse.urlparse(self.link).hostname
        external_link = flask.get_template_attribute("components/links.html", "external_link")
        return external_link(href=self.link, text=text)


@dataclasses.dataclass()
class CollectionProperty(BaseProperty):
    name: str
    items: typing.Collection[typing.Any] = None
    sorted: bool = False

    def __bool__(self) -> bool:
        return bool(self.items)

    def __iter__(self):
        return sorted(self.items) if self.sorted else iter(self.items)

    def __str__(self) -> str:
        render = flask.get_template_attribute("components/metadata.html", "list_property")
        return render(property=self)


@dataclasses.dataclass()
class JsonProperty(BaseProperty):
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
class Source:
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


class IntoSource:
    @classmethod
    def into_source(self) -> Source:
        raise NotImplementedError()


@dataclasses.dataclass(kw_only=True)
class Details(IntoProperties):
    """Details describe static information about a work."""

    title: str = None
    author: str = None
    description: str = None
    release_date: datetime.date = None
    cover: str = None
    background: str = None
    shelf: Shelf = None
    tags: typing.Set[str] = dataclasses.field(default_factory=set)
    external_url: str = None

    def __str__(self) -> str:
        d = f"{self.title}"

        if self.author:
            d += f", {self.author}"

        if self.release_date:
            d += f" ({self.release_date.year})"

        return d

    def into_properties(self) -> typing.Iterable[Property]:
        yield Property("Title", self.title)
        yield Property("Author", self.author)
        yield Property("Release date", self.release_date)
        yield Property("Shelf", self.shelf.title if self.shelf else None)
        yield CollectionProperty("Tags", self.tags)

    def more_properties(self) -> typing.Iterable[Property]:
        yield UrlProperty("Cover", self.cover)
        yield UrlProperty("Background", self.background)


class IntoDetails:
    def into_details(self) -> Details:
        raise NotImplementedError()
