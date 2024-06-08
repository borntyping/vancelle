import svcs

from .base import Manager
from ...clients.goodreads.http import GoodreadsPublicScraper
from ...lib.pagination import Pagination

from ...models.remote import GoodreadsPrivateBook, GoodreadsPublicBook
from ...models.work import Book


class GoodreadsPrivateBookManager(Manager):
    remote_type = GoodreadsPrivateBook
    work_type = Book

    def fetch(self, remote_id: str) -> GoodreadsPrivateBook:
        raise NotImplementedError("Private Goodreads books cannot be fetched.")

    def search(self, query: str) -> Pagination[GoodreadsPrivateBook]:
        raise NotImplementedError("Private Goodreads books cannot be searched.")


class GoodreadsPublicBookManager(Manager):
    remote_type = GoodreadsPublicBook
    work_type = Book

    def fetch(self, remote_id: str) -> GoodreadsPublicBook:
        goodreads = svcs.flask.get(GoodreadsPublicScraper)
        return goodreads.fetch(remote_id)

    def search(self, query: str) -> Pagination[GoodreadsPublicBook]:
        goodreads = svcs.flask.get(GoodreadsPublicScraper)
        return Pagination.from_iterable(goodreads.search(query))
