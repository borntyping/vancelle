import dataclasses
import datetime
import typing

import flask
import hotmetal
import structlog

from vancelle.html.document import span
from vancelle.html.types import Hotmetal
from vancelle.html.vancelle.components.metadata import absent, external_url, internal_url
from vancelle.inflect import p

logger = structlog.get_logger(logger_name=__name__)


class Property:
    name: str
    description: str | None

    def __bool__(self) -> bool:
        raise NotImplementedError

    def __str__(self) -> str:
        if not self:
            return hotmetal.render(absent())

        return hotmetal.render(self.html())

    def html(self) -> Hotmetal:
        raise NotImplementedError

    @staticmethod
    def macro(attribute: str, **context: typing.Any) -> str:
        render = flask.get_template_attribute("components/metadata.html", attribute)
        return render(**context)


@dataclasses.dataclass()
class StringProperty(Property):
    name: str
    value: str | typing.Any
    description: str | None = None

    def __bool__(self) -> bool:
        return bool(self.value)

    def html(self) -> Hotmetal:
        return span({}, str(self.value))


@dataclasses.dataclass()
class TimeProperty(Property):
    name: str
    value: datetime.datetime | datetime.date | typing.Any
    description: str | None = None

    def __bool__(self) -> bool:
        return self.value is not None

    def html(self) -> Hotmetal:
        return span({}, str(self.value))


@dataclasses.dataclass()
class InternalUrlProperty(Property):
    name: str
    link: str | None
    text: str | None = None
    description: str | None = None

    def __bool__(self) -> bool:
        return bool(self.link or self.text)

    def html(self) -> Hotmetal:
        return internal_url(href=self.link, text=self.text)


@dataclasses.dataclass()
class ExternalUrlProperty(Property):
    name: str
    link: str | None
    text: str | None = None
    description: str | None = None

    def __bool__(self) -> bool:
        return bool(self.link or self.text)

    def html(self) -> Hotmetal:
        return external_url(href=self.link, text=self.text)


@dataclasses.dataclass()
class IterableProperty(Property):
    name: str
    items: typing.Iterable[typing.Any] = ()
    sorted: bool = False
    description: str | None = None

    def __bool__(self) -> bool:
        return bool(self.items)

    def __iter__(self):
        return sorted(self.items) if self.sorted else iter(self.items)

    def html(self) -> Hotmetal:
        return span({}, p.join([str(item) for item in self]))


class IntoProperties:
    def into_properties(self) -> typing.Iterable[Property]:
        return ()

    def more_properties(self) -> typing.Iterable[Property]:
        return ()
