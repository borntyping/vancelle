from .base import Manager
from ...ext.flask_sqlalchemy import Pagination, ItemsPagination
from ...extensions import apis
from ...models import RoyalroadFiction


class RoyalroadFictionManager(Manager):
    remote_type = RoyalroadFiction

    def fetch(self, remote_id: str) -> RoyalroadFiction:
        return apis.royalroad.fiction(remote_id=remote_id)

    def search(self, query: str) -> Pagination[RoyalroadFiction]:
        items = apis.royalroad.search_fictions(title=query)
        return ItemsPagination(page=1, per_page=len(items), items=items, total=len(items))
