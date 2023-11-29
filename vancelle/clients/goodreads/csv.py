import csv
import datetime
import pathlib
import re
import typing

import structlog

from .common import GoodreadsImporter
from .types import GoodreadsCsvRow
from ...models.remote import GoodreadsBook
from ...types import Sentinel, sentinel

logger = structlog.get_logger(logger_name=__name__)


T = typing.TypeVar("T")


class GoodreadsCsvImporter(GoodreadsImporter):
    def load_file(self, path: pathlib.Path) -> list[GoodreadsBook]:
        with path.open("r") as f:
            rows = csv.DictReader(f)
            return [self.parse_row(typing.cast(GoodreadsCsvRow, row), filename=path.name) for row in rows]

    def load_stream(self, stream: typing.IO[bytes], filename: str) -> list[GoodreadsBook]:
        rows = csv.DictReader((line.decode("utf-8") for line in stream))
        return [self.parse_row(typing.cast(GoodreadsCsvRow, row), filename=filename) for row in rows]

    def parse_row(self, row: GoodreadsCsvRow, *, filename: str) -> GoodreadsBook:
        id = self.parse_string(row["Book Id"])
        title = self.parse_string(row["Title"])
        author = self.parse_string(row["Author"])

        bookshelves = self.parse_bookshelves(row["Bookshelves"])
        exclusive_shelf = self.parse_string(row["Exclusive Shelf"])
        date_published_edition = self.parse_date_optional(row["Year Published"], "%Y")
        date_published_work = self.parse_date_optional(row["Original Publication Year"], "%Y")
        release_date = date_published_edition or date_published_work or None
        shelf = self.parse_shelf(exclusive_shelf, release_date)

        date_read = self.parse_date_optional(row["Date Read"])
        isbn13 = self.parse_isbn(row["ISBN13"])

        return self._create_or_update(
            remote_id=id,
            title=title,
            author=author,
            release_date=release_date,
            cover=None,
            shelf=shelf,
            tags=set(bookshelves),
            date_started=None,
            date_stopped=date_read,
            isbn13=isbn13,
            data={
                "csv_filename": filename,
                "csv": row,
            },
        )

    @staticmethod
    def parse_isbn(value: str) -> str | None:
        """
        >>> instance = GoodreadsCsvImporter({}, None)
        >>> instance.parse_isbn('="0786818611"')
        '0786818611'
        >>> instance.parse_isbn('="9780786818617"')
        '9780786818617'
        >>> instance.parse_isbn('=""')
        """
        if value == '=""':
            return None

        if match := re.match('="(.+)"', value):
            return match.group(1)

        raise ValueError(f"Could not parse {value}")

    @staticmethod
    def parse_date(value: str, fmt: str = "%Y/%m/%d") -> datetime.date:
        """
        >>> instance = GoodreadsCsvImporter({}, None)
        >>> instance.parse_date("2017/08/24")
        datetime.date(2017, 8, 24)
        """
        return datetime.datetime.strptime(value, fmt).date()

    def parse_date_optional(self, value: str | None, fmt: str = "%Y/%m/%d") -> datetime.date | None:
        """
        >>> instance = GoodreadsCsvImporter({}, None)
        >>> instance.parse_date_optional("")
        """
        return self.parse_date(value, fmt) if value else None

    @staticmethod
    def parse_int(value: str) -> int:
        """
        >>> instance = GoodreadsCsvImporter({}, None)
        >>> instance.parse_int("2022")
        2022
        """
        return int(value)

    def parse_int_optional(self, value: str) -> int | None:
        """
        >>> instance = GoodreadsCsvImporter({}, None)
        >>> instance.parse_int_optional("")
        """
        return self.parse_int(value) if value else None

    @staticmethod
    def parse_bookshelves(value: str) -> list[str]:
        """
        >>> instance = GoodreadsCsvImporter({}, None)
        >>> instance.parse_bookshelves('gave-up-on')
        ['gave-up-on']
        >>> instance.parse_bookshelves('want-to-read-next, to-read')
        ['want-to-read-next', 'to-read']
        """
        if value == "":
            return []

        return [s.strip() for s in value.split(",")]

    @classmethod
    def parse_bookshelves_with_positions(cls, value: str) -> dict[str, int]:
        """
        >>> instance = GoodreadsCsvImporter({}, None)
        >>> instance.parse_bookshelves_with_positions('to-read (#194)')
        {'to-read': 194}
        """
        if value == "":
            return {}

        return dict(cls.parse_bookshelf(s.strip()) for s in value.split(","))

    @staticmethod
    def parse_bookshelf(value: str) -> typing.Tuple[str, int]:
        if match := re.match(r"([\w-]+) \(#(\d+)\)", value):
            name = match.group(1)
            rank = match.group(2)
            return name, int(rank)

        raise ValueError(f"Could not parse bookshelf {value!r}")

    @staticmethod
    def parse_string(value: str, default: T | Sentinel = sentinel) -> str | T:
        if not value:
            if not isinstance(default, Sentinel):
                return default
            raise ValueError("Empty string")
        return value
