from .base import Manager
from ...ext.flask_sqlalchemy import Pagination, ItemsPagination
from ...extensions import apis
from ...models.remote import RoyalroadFiction
from ...models.work import Book


class RoyalroadFictionManager(Manager):
    remote_type = RoyalroadFiction
    work_type = Book

    def fetch(self, remote_id: str) -> RoyalroadFiction:
        return apis.royalroad.fiction(remote_id=remote_id)

    def search(self, query: str) -> Pagination[RoyalroadFiction]:
        items = apis.royalroad.search_fictions(title=query)
        return ItemsPagination(page=1, per_page=len(items), items=items, total=len(items), error_out=False)
