import dataclasses
import datetime
import pathlib
import re
import types
import typing

import bs4
import bs4.element
import structlog

from .common import GoodreadsImporter
from ...models.remote import GoodreadsPrivateBook
from ...types import Sentinel, sentinel

logger = structlog.get_logger(logger_name=__name__)

T = typing.TypeVar("T")


whitespace = re.compile(r"\s+")
separator = re.compile(r",\s+")


@dataclasses.dataclass()
class Field:
    """This is overkill, but really helps when debugging parsing."""

    name: str
    field: bs4.element.Tag
    value: bs4.element.Tag

    def __enter__(self) -> bs4.element.Tag:
        return self.value

    def __exit__(
        self,
        exc_type: typing.Type[BaseException] | None,
        exc: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        if exc is not None:
            logger.error(
                "Unexpected exception while parsing field",
                name=self.name,
                field=str(self.field.prettify()),
                value=str(self.value.prettify()),
                exc_info=(exc_type, exc, traceback),
            )


@dataclasses.dataclass(frozen=True)
class GoodreadsHtmlImporter(GoodreadsImporter):
    def load_file(self, path: pathlib.Path) -> typing.Iterable[GoodreadsPrivateBook]:
        with path.open("r") as f:
            yield from self.parse_markup(markup=f, filename=path.name)

    def parse_markup(
        self, markup: str | typing.IO[str] | typing.IO[bytes], *, filename: str
    ) -> typing.Iterable[GoodreadsPrivateBook]:
        log = logger.bind(filename=filename)

        log.debug("Making soup")
        soup = bs4.BeautifulSoup(markup=markup, features="html.parser")

        log.debug("Finding table rows")
        elements = soup.find("tbody", id="booksBody").find_all("tr", {"class": "bookalike"})

        log.debug("Parsing table rows", elements=len(elements))

        for e in elements:
            yield self.parse_row(e, filename=filename)

    def parse_row(self, element: bs4.Tag, filename: str) -> GoodreadsPrivateBook:
        with self.field(element, "cover") as tag:
            cover: str = tag.find("img").attrs.get("src")

        with self.field(element, "title") as tag:
            title: str = self.parse_string(tag.find("a"))

        with self.field(element, "author") as tag:
            author: str = self.parse_author(self.parse_string(tag.find("a")))

        with self.field(element, "isbn") as tag:
            isbn10: str | None = self.parse_string(tag, default=None)

        with self.field(element, "isbn13") as tag:
            isbn13: str | None = self.parse_string(tag, default=None)

        with self.field(element, "asin") as tag:
            asin: str | None = self.parse_string(tag, default=None)

        with self.field(element, "num_pages") as tag:
            num_pages: int | None = None
            if nobr := tag.find("nobr"):
                num_pages = self.parse_int(self.parse_string(nobr, default=None))

        with self.field(element, "avg_rating") as tag:
            avg_rating: str | None = self.parse_string(tag)

        # num_ratings

        with self.field(element, "date_pub") as tag:
            date_pub_str: str | None = self.parse_string(tag, default=None)
            date_pub: datetime.date | None = self.parse_date(date_pub_str)

        with self.field(element, "date_pub_edition") as tag:
            date_pub_edition_str: str | None = self.parse_string(tag, default=None)
            date_pub_edition: datetime.date | None = self.parse_date(date_pub_edition_str)

        with self.field(element, "rating") as tag:
            stars = tag.find("div", {"class": "stars"})
            resource_id: str = self.parse_id(stars.attrs.get("data-resource-id"))
            rating: int = self.parse_int(stars.attrs.get("data-rating"))

        with self.field(element, "shelves") as tag:
            shelves: list[str] = [e.string.strip() for e in tag.find_all("a", {"class": "shelfLink"})]
            exclusive_shelf = shelves[0] if shelves else None

        # review
        # notes
        # comments
        # votes

        with self.field(element, "read_count") as tag:
            read_count: int = self.parse_int(self.parse_string(tag, default="0"))

        with self.field(element, "date_started") as tag:
            date_started_str: str | None = None
            date_started: datetime.date | None = None
            if subtag := tag.find("span", class_="date_started_value"):
                date_started_str = self.parse_string(subtag)
                date_started = self.parse_date(date_started_str)

        with self.field(element, "date_read") as tag:
            date_read_str: str | None = None
            date_read: datetime.date | None = None
            if subtag := tag.find("span", class_="date_read_value"):
                date_read_str = self.parse_string(subtag)
                date_read = self.parse_date(date_read_str)

        with self.field(element, "date_added") as tag:
            date_added_str = self.parse_string(tag.find("span"))
            date_added: datetime.date | None = self.parse_date(date_added_str)

        with self.field(element, "owned") as tag:
            owned: int = self.parse_int(self.parse_string(tag, default="0"))

        with self.field(element, "format") as tag:
            binding: str | None = self.parse_string(tag, default=None)

        release_date = date_pub_edition or date_pub or None
        shelf = self.parse_shelf(exclusive_shelf, release_date)

        return self._create_or_update(
            remote_id=resource_id,
            title=title,
            author=author,
            release_date=release_date,
            cover=cover,
            shelf=shelf,
            tags=set(shelves),
            isbn13=isbn13,
            date_started=date_started,
            date_stopped=date_read,
            data={
                "asin": asin,
                "html_filename": filename,
                "html": {
                    "cover": cover,
                    "title": title,
                    "author": author,
                    "isbn10": isbn10,
                    "isbn13": isbn13,
                    "asin": asin,
                    "num_pages": num_pages,
                    "avg_rating": avg_rating,
                    "date_pub": date_pub_str,
                    "date_pub_edition": date_pub_edition_str,
                    "resource_id": resource_id,
                    "rating": rating,
                    "shelves": shelves,
                    "exclusive_shelf": exclusive_shelf,
                    "read_count": read_count,
                    "date_started": date_started_str,
                    "date_read": date_read_str,
                    "date_added": date_added_str,
                    "owned": owned,
                    "binding": binding,
                },
            },
        )

    def field(self, element: bs4.Tag, name: str) -> Field:
        field = element.find("td", {"class": f"field {name}"})
        if not isinstance(field, bs4.element.Tag):
            raise Exception(f"Field {name} not found")

        value = field.find("div", {"class": "value"})
        if not isinstance(value, bs4.element.Tag):
            raise Exception(f"Value for field {name} not found")

        return Field(name, field, value)

    @staticmethod
    def parse_id(value: str) -> str:
        if not value:
            raise Exception(f"Missing ID: {value!r}")
        return value

    @typing.overload
    def parse_string(self, element: bs4.element.Tag | None) -> str: ...

    @typing.overload
    def parse_string(self, element: bs4.element.Tag | None, default: str) -> str: ...

    @typing.overload
    def parse_string(self, element: bs4.element.Tag | None, default: None) -> str | None: ...

    def parse_string(self, element: bs4.element.Tag | None, default: str | None | Sentinel = sentinel) -> str | None:
        if element is None:
            raise AttributeError("Element is None")

        if not element.contents:
            if not isinstance(default, Sentinel):
                return default

            raise AttributeError(f"Element is empty: {element}")

        child = element.contents[0]

        if not isinstance(child, str):
            raise AttributeError(f"First child is not a string in {element}")

        string = child.strip()

        if string == "":
            if not isinstance(default, Sentinel):
                return default

            raise AttributeError(f"Element contains an empty string")

        return whitespace.sub(" ", string)

    @staticmethod
    def parse_date(value: str | None) -> datetime.date | None:
        if value is None:
            return None

        for date_format in ["%b %d, %Y", "%b %Y", "%Y"]:
            try:
                return datetime.datetime.strptime(value, date_format).date()
            except ValueError:
                pass

        logger.warning("Could not parse date", value=repr(value))
        return None

    @typing.overload
    def parse_int(self, value: str) -> int: ...

    @typing.overload
    def parse_int(self, value: str | None) -> int | None: ...

    def parse_int(self, value):
        if value is None:
            return None

        integer = int(value.replace(",", ""))

        if not integer >= 0:
            raise ValueError(f"Expected integer to be positive, got {integer}")

        return integer

    @staticmethod
    def parse_author(value: str) -> str:
        """
        >>> GoodreadsHtmlImporter.parse_author('Hanna, K.T.')
        'K.T. Hanna'
        >>> GoodreadsHtmlImporter.parse_author('Kloos, Marko')
        'Marko Kloos'
        >>> GoodreadsHtmlImporter.parse_author('Sriduangkaew, Benjanun')
        'Benjanun Sriduangkaew'
        """
        return " ".join(reversed(separator.split(value, maxsplit=1)))
