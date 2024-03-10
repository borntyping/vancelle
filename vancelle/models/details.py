import dataclasses
import datetime
import typing

import structlog

from vancelle.models.properties import ExternalUrlProperty, IntoProperties, IterableProperty, Property, StringProperty

logger = structlog.get_logger(logger_name=__name__)


@dataclasses.dataclass(kw_only=True)
class Details(IntoProperties):
    """Details describe static information about a work."""

    title: str | None
    author: str | None
    series: str | None
    description: str | None
    release_date: datetime.date | None
    cover: str | None
    background: str | None
    tags: typing.Set[str] | None = dataclasses.field(default_factory=set)
    external_url: str | None

    def __bool__(self) -> bool:
        return any(dataclasses.astuple(self))

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
        yield StringProperty("Series", self.series)
        yield StringProperty("Release date", self.release_date)
        yield IterableProperty("Tags", list(self.tags) if self.tags else ())
        yield ExternalUrlProperty("External URL", self.external_url)


class IntoDetails:
    def into_details(self) -> Details:
        raise NotImplementedError()
