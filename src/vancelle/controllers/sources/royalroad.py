import svcs

from .base import Source
from ...clients.royalroad.client import RoyalRoadScraper
from ...lib.pagination import Pagination
from ...models.entry import RoyalroadFiction
from ...models.work import Book


class RoyalroadFictionSource(Source):
    entry_type = RoyalroadFiction
    work_type = Book

    def fetch(self, entry_id: str) -> RoyalroadFiction:
        client = svcs.flask.get(RoyalRoadScraper)
        return client.fiction(id=entry_id)

    def search(self, query: str) -> Pagination[RoyalroadFiction]:
        client = svcs.flask.get(RoyalRoadScraper)
        items = client.search_fictions(title=query)
        return Pagination.from_iterable(items)
