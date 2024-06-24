import svcs

from .base import Source
from ...clients.goodreads.http import GoodreadsPublicScraper
from ...lib.pagination import Pagination

from ...models.entry import GoodreadsPrivateBook, GoodreadsPublicBook
from ...models.work import Book


class GoodreadsPrivateBookSource(Source):
    entry_type = GoodreadsPrivateBook
    work_type = Book

    def fetch(self, entry_id: str) -> GoodreadsPrivateBook:
        raise NotImplementedError("Private Goodreads books cannot be fetched.")

    def search(self, query: str) -> Pagination[GoodreadsPrivateBook]:
        raise NotImplementedError("Private Goodreads books cannot be searched.")


class GoodreadsPublicBookSource(Source):
    entry_type = GoodreadsPublicBook
    work_type = Book

    def fetch(self, entry_id: str) -> GoodreadsPublicBook:
        goodreads = svcs.flask.get(GoodreadsPublicScraper)
        return goodreads.fetch(entry_id)

    def search(self, query: str) -> Pagination[GoodreadsPublicBook]:
        goodreads = svcs.flask.get(GoodreadsPublicScraper)
        return Pagination.from_iterable(goodreads.search(query))
