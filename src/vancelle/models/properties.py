import dataclasses
import datetime
import typing

import flask
import hotmetal
import humanize
import structlog

from vancelle.lib.heavymetal.html import abbr, code, span
from vancelle.lib.heavymetal import Heavymetal
from vancelle.html.vancelle.components.metadata import external_url, internal_url
from vancelle.html.vancelle.components.optional import span_absent
from vancelle.inflect import p
from vancelle.shelf import Shelf

logger = structlog.get_logger(logger_name=__name__)


Properties = typing.Sequence["Property"]


@dataclasses.dataclass()
class Property:
    name: str
    title: str | None = dataclasses.field(default=None, kw_only=True)

    def __bool__(self) -> bool:
        return True

    def __str__(self) -> str:
        if not self:
            return hotmetal.render(span_absent())

        return hotmetal.render(self.heavymetal())

    def heavymetal(self) -> Heavymetal:
        raise NotImplementedError

    @staticmethod
    def macro(attribute: str, **context: typing.Any) -> str:
        render = flask.get_template_attribute("components/metadata.html", attribute)
        return render(**context)


@dataclasses.dataclass()
class StringProperty(Property):
    value: str | typing.Any

    def __bool__(self) -> bool:
        return bool(self.value)

    def heavymetal(self) -> Heavymetal:
        return span({}, str(self.value))


@dataclasses.dataclass()
class CodeProperty(Property):
    value: str | typing.Any

    def __bool__(self) -> bool:
        return bool(self.value)

    def heavymetal(self) -> Heavymetal:
        return code({}, str(self.value))


@dataclasses.dataclass()
class DatetimeProperty(Property):
    value: datetime.datetime | datetime.date | None

    def __bool__(self) -> bool:
        return self.value is not None

    def heavymetal(self) -> Heavymetal:
        return abbr({"title": str(self.value)}, humanize.naturaltime(self.value)) if self.value else span_absent()


@dataclasses.dataclass()
class InternalUrlProperty(Property):
    link: str
    text: str

    def __bool__(self) -> bool:
        return bool(self.link and self.text)

    def heavymetal(self) -> Heavymetal:
        return internal_url(href=self.link, text=self.text)


@dataclasses.dataclass()
class ExternalUrlProperty(Property):
    link: str | None
    text: str | None = None

    def __bool__(self) -> bool:
        return bool(self.link or self.text)

    def heavymetal(self) -> Heavymetal:
        return external_url(href=self.link, text=self.text)


@dataclasses.dataclass()
class IterableProperty(Property):
    items: typing.Iterable[typing.Any] = ()
    sorted: bool = False

    def __bool__(self) -> bool:
        return bool(self.items)

    def __iter__(self):
        return sorted(self.items) if self.sorted else iter(self.items)

    def heavymetal(self) -> Heavymetal:
        return span({}, p.join([str(item) for item in self]))


@dataclasses.dataclass()
class ShelfProperty(Property):
    shelf: Shelf

    def heavymetal(self) -> Heavymetal:
        return abbr({"title": self.shelf.description}, self.shelf.title)


class IntoProperties:
    def into_properties(self) -> typing.Iterable[Property]:
        return ()

    def more_properties(self) -> typing.Iterable[Property]:
        return ()
