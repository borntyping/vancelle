import typing

from .base import Manager
from ...ext.flask_sqlalchemy import Pagination, StaticPagination
from ...extensions import apis
from ...models.remote import OpenlibraryEdition, OpenlibraryWork
from ...models.work import Book


class OpenlibraryWorkManager(Manager):
    remote_type = OpenlibraryWork
    work_type = Book

    def fetch(self, remote_id: str) -> OpenlibraryWork:
        return apis.openlibrary.work(id=remote_id)

    def search(self, query: str) -> Pagination[OpenlibraryWork]:
        return StaticPagination(items=apis.openlibrary.search(q=query))

    def context(self, remote: OpenlibraryWork) -> typing.Mapping[str, typing.Any]:
        return {"editions": apis.openlibrary.work_editions(remote.id)}


class OpenlibraryEditionManager(Manager):
    remote_type = OpenlibraryEdition
    work_type = Book

    def fetch(self, remote_id: str) -> OpenlibraryEdition:
        return apis.openlibrary.edition(id=remote_id)

    def search(self, query: str) -> Pagination[OpenlibraryEdition]:
        raise NotImplementedError
