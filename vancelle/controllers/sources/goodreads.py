import typing

from .base import Manager
from ...ext.flask_sqlalchemy import Pagination
from ...models.remote import GoodreadsBook


class GoodreadsBookManager(Manager):
    remote_type = GoodreadsBook

    def fetch(self, remote_id: str) -> GoodreadsBook:
        raise NotImplementedError

    def search(self, query: str) -> Pagination[GoodreadsBook]:
        raise NotImplementedError
