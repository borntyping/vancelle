import svcs

from .base import Manager
from ...clients.goodreads.http import GoodreadsPublicScraper
from ...ext.flask_sqlalchemy import ItemsPagination, Pagination
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
        items = list(goodreads.search(query))
        return ItemsPagination(page=1, per_page=len(items), items=items, total=len(items), error_out=False)
