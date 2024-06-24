import typing

import svcs

from .base import Source
from ...clients.openlibrary.client import OpenLibraryAPI
from ...lib.pagination import Pagination
from ...models.entry import OpenlibraryEdition, OpenlibraryWork
from ...models.work import Book


class OpenlibraryWorkSource(Source):
    entry_type = OpenlibraryWork
    work_type = Book

    def fetch(self, entry_id: str) -> OpenlibraryWork:
        openlibrary = svcs.flask.get(OpenLibraryAPI)
        return openlibrary.work(id=entry_id)

    def search(self, query: str) -> Pagination[OpenlibraryWork]:
        openlibrary = svcs.flask.get(OpenLibraryAPI)
        return Pagination.from_iterable(openlibrary.search(q=query))

    def context(self, entry: OpenlibraryWork) -> typing.Mapping[str, typing.Any]:
        openlibrary = svcs.flask.get(OpenLibraryAPI)
        return {"editions": openlibrary.work_editions(entry.id)}


class OpenlibraryEditionSource(Source):
    entry_type = OpenlibraryEdition
    work_type = Book

    def fetch(self, entry_id: str) -> OpenlibraryEdition:
        openlibrary = svcs.flask.get(OpenLibraryAPI)
        return openlibrary.edition(id=entry_id)

    def search(self, query: str) -> Pagination[OpenlibraryEdition]:
        raise NotImplementedError
