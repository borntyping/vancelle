import dataclasses
import datetime
import typing

import flask
import structlog

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

        return self.macro("internal_url", href=self.link, text=self.text)


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

        return self.macro("external_url", href=self.link, text=self.text)


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
