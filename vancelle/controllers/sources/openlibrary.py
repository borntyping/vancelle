import typing

import svcs

from .base import Manager
from ...clients.openlibrary.client import OpenLibraryAPI
from ...ext.flask_sqlalchemy import Pagination, StaticPagination
from ...models.remote import OpenlibraryEdition, OpenlibraryWork
from ...models.work import Book


class OpenlibraryWorkManager(Manager):
    remote_type = OpenlibraryWork
    work_type = Book

    def fetch(self, remote_id: str) -> OpenlibraryWork:
        openlibrary = svcs.flask.get(OpenLibraryAPI)
        return openlibrary.work(id=remote_id)

    def search(self, query: str) -> Pagination[OpenlibraryWork]:
        openlibrary = svcs.flask.get(OpenLibraryAPI)
        return StaticPagination(items=openlibrary.search(q=query))

    def context(self, remote: OpenlibraryWork) -> typing.Mapping[str, typing.Any]:
        openlibrary = svcs.flask.get(OpenLibraryAPI)
        return {"editions": openlibrary.work_editions(remote.id)}


class OpenlibraryEditionManager(Manager):
    remote_type = OpenlibraryEdition
    work_type = Book

    def fetch(self, remote_id: str) -> OpenlibraryEdition:
        openlibrary = svcs.flask.get(OpenLibraryAPI)
        return openlibrary.edition(id=remote_id)

    def search(self, query: str) -> Pagination[OpenlibraryEdition]:
        raise NotImplementedError
