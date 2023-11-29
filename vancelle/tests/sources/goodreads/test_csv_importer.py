import datetime
import pathlib
import uuid

from vancelle.models import User
from vancelle.models.remote import GoodreadsBook
from vancelle.models.record import Record
from vancelle.types import Shelf
from vancelle.clients.goodreads.csv import GoodreadsCsvImporter


class MockGoodreadsCsvImporter(GoodreadsCsvImporter):
    def get_remote(self, remote_id: str) -> GoodreadsBook | None:
        return None

    def get_record(self, record_id: uuid.UUID) -> Record | None:
        return None


class TestGoodreadsCsvImporter:
    def test_load(self, fixtures: pathlib.Path):
        path = fixtures / "goodreads-1.csv"
        importer = MockGoodreadsCsvImporter(
            shelf_mapping={"read": Shelf.COMPLETED},
            user=User(id=uuid.uuid4(), username="example", password=""),
        )
        books = list(importer.load_file(path))

        assert books, "No books returned"
        assert books[0].id == "58669149"
        assert books[0].title == "Centers of Gravity (Frontlines, #8)"
        assert books[0].author == "Marko Kloos"
        assert books[0].release_date == datetime.date(2022, 1, 1)
        assert books[0].cover is None
        assert books[0].work.records[0].date_started is None
        assert books[0].work.records[0].date_stopped == datetime.date(2023, 10, 22)
        assert books[0].tags == ["read"]
        assert books[0].shelf == Shelf.COMPLETED
        assert books[0].data["csv_filename"] == path.name
