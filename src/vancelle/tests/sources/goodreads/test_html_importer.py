import datetime
import pathlib
import uuid

import pytest

from vancelle.models import User
from vancelle.models.entry import GoodreadsPrivateBook
from vancelle.models.record import Record
from vancelle.shelf import Shelf
from vancelle.clients.goodreads.html import GoodreadsHtmlImporter


class MockGoodreadsHtmlImporter(GoodreadsHtmlImporter):
    def get_entry(self, entry_id: str) -> GoodreadsPrivateBook | None:
        return None

    def get_record(self, record_id: uuid.UUID) -> Record | None:
        return None


@pytest.mark.parametrize(
    "d",
    [
        "1984",
        "1990",
        "2000",
        "Jun 2011",
        "Jun 2023",
        "Oct 2009",
    ],
)
def test_parse_date(d: str):
    assert MockGoodreadsHtmlImporter.parse_date(d)


def test_html_import_tr(fixtures: pathlib.Path):
    path = fixtures / "goodreads-1.html"
    importer = MockGoodreadsHtmlImporter(
        shelf_mapping={"read": Shelf.COMPLETED},
        user=User(id=uuid.uuid4(), username="example", password=""),
    )
    books = list(importer.load_file(path))

    assert books, "No books returned"
    assert books[0].id == "58669149"
    assert books[0].title == "Centers of Gravity"
    assert books[0].author == "Marko Kloos"
    assert books[0].release_date == datetime.date(2022, 8, 30)
    assert books[0].cover
    assert books[0].cover.startswith("https://i.gr-assets.com")
    assert books[0].work.records[0].date_started == datetime.date(2023, 10, 18)
    assert books[0].work.records[0].date_stopped == datetime.date(2023, 10, 22)
    assert books[0].tags == {"read"}
    assert books[0].shelf == Shelf.COMPLETED
    assert books[0].data
    assert books[0].data["asin"] == "B099RVRQJ1"
    assert books[0].data["html_filename"] == path.name
