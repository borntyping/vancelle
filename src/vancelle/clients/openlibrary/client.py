import dataclasses
import datetime
import typing

import flask
import hishel
import structlog
import svcs

from vancelle.clients.client import HttpClient, HttpClientBuilder
from vancelle.clients.common import parse_date
from vancelle.clients.openlibrary.types import (
    Author,
    Edition,
    KeyType,
    Reference,
    Search,
    Size,
    Work,
    WorkEditions,
)
from vancelle.models.remote import OpenlibraryEdition, OpenlibraryWork

logger = structlog.get_logger(logger_name=__name__)


class OpenLibraryAPI(HttpClient):
    @classmethod
    def factory(cls, svcs_container: svcs.Container) -> typing.Self:
        builder = svcs_container.get(HttpClientBuilder)
        return cls(client=hishel.CacheClient(storage=builder.sqlite_storage_for(cls)))

    def search(self, q: str) -> list[OpenlibraryWork]:
        """
        Open Library Search API.

        https://openlibrary.org/dev/docs/api/search
        """
        response = self.get("https://openlibrary.org/search.json", params={"q": q})
        data: Search = response.json()

        logger.info("Searched Open Library", numFound=data["numFound"])

        return [
            OpenlibraryWork(
                id=self.parse_key("works", doc["key"]),
                title=doc["title"],
                author=", ".join(doc.get("author_name", [])),
                data={
                    "url": response.url,
                    "doc": data,
                },
            )
            for doc in data["docs"]
        ]

    def work(self, id: str):
        """
        Part of the Works API. Returns information about a specific work.

        https://openlibrary.org/dev/docs/api/books
        https://openlibrary.org/works/OL20861787W.json
        """
        assert isinstance(id, str)

        response = self.get(f"https://openlibrary.org/works/{id}.json")
        data: Work = response.json()

        id = self.parse_key("works", data["key"])
        title = data["title"]
        author = self._author_references([author["author"] for author in data["authors"]])
        description = data.get("description", {}).get("value")
        cover = self.cover_url("ID", data["covers"][0]) if data.get("covers") else None

        return OpenlibraryWork(
            id=id,
            title=title,
            author=author,
            description=description,
            cover=cover,
            data={"url": response.url, "work": data},
        )

    def _author_references(self, references: list[Reference]) -> str:
        keys = (self.parse_key("authors", ref["key"]) for ref in references)
        authors = (self.author(key) for key in keys)
        names = (author["name"] for author in authors)
        return ", ".join(names)

    def work_editions(self, id: str) -> list[OpenlibraryEdition]:
        """
        Part of the Works API. Returns a list of editions associated with a work.
        Don't mix this up with the Editions API, which uses '/books/'.

        https://openlibrary.org/dev/docs/api/books
        https://openlibrary.org/works/OL20861787W/editions.json
        """
        response = self.get(f"https://openlibrary.org/works/{id}/editions.json")
        editions: WorkEditions = response.json()

        logger.info("Fetched editions from Open Library", entries=len(editions["entries"]))
        return [self._edition(edition, url=str(response.url)) for edition in editions["entries"]]

    def edition(self, id: str) -> OpenlibraryEdition:
        """
        Part of the Editions API. Returns info about a specific edition of a work.

        https://openlibrary.org/dev/docs/api/books
        https://openlibrary.org/books/OL34257970M.json
        https://openlibrary.org/books/OL7353617M.json
        """
        response = self.get(f"https://openlibrary.org/books/{id}.json")
        edition: Edition = response.json()

        logger.info("Fetched edition from Open Library", url=response.request.url)
        return self._edition(edition, url=str(response.url))

    def _edition(self, edition: Edition, *, url: str | None = None) -> OpenlibraryEdition:
        if len(edition["works"]) != 1:
            raise Exception(f"Unexpected number of works connected to this edition: {edition['works']}")

        id = self.parse_key("books", edition["key"])
        _work_id = self.parse_key("works", edition["works"][0]["key"])
        _goodreads_id = edition.get("identifiers", {}).get("goodreads", None)
        _librarything_id = edition.get("identifiers", {}).get("librarything", None)
        title = edition["title"]
        author = self._author_references(edition.get("authors", []))
        _publish_date = self.parse_date(edition.get("publish_date", None))
        _first_sentence = edition.get("first_sentence", None)
        _number_of_pages = edition.get("number_of_pages", None)
        isbn_13s = edition.get("isbn_13", [])
        covers = edition.get("covers", [])

        isbn_13 = isbn_13s[0] if isbn_13s else None
        cover = self.cover_url("ID", covers[0]) if covers else None

        return OpenlibraryEdition(
            id=id,
            title=title,
            author=author,
            cover=cover,
            data={
                "url": url,
                "isbn13": isbn_13,
                "edition": edition,
            },
        )

    def author(self, id: str) -> Author:
        """
        TODO: This needs some form of nice cache, handle the case where we fetch a work
        TODO: and edition in the same request.

        https://openlibrary.org/authors/OL1425963A.json
        """
        response = self.session.get(f"https://openlibrary.org/authors/{id}.json")
        response.raise_for_status()
        author = response.json()
        return author

    @staticmethod
    def parse_key(category: str, key: str):
        """
        The Search API returns references in `/work/{olid}` format, but we want to
        store and use the work ID. Storing and using the path-style "api_key" is painful
        both when writing a client for the Open Library API (as keys are appended
        directly to the domain name) and when writing routes (as Flask doesn't love
        paths in routes, and often stripped the first slash in my experience).

        https://openlibrary.org/search.json?q=To+Sleep+in+a+Sea+of+Stars
        """
        prefix = f"/{category}/"
        if not key.startswith(prefix):
            raise ValueError(f"Expected Openlibrary api_key '{key}' to start with '{prefix}'.")
        return key.removeprefix(prefix)

    @staticmethod
    def parse_date(string: str | None) -> datetime.date | None:
        return parse_date(string, ("%b %d, %Y", "%Y"))

    @staticmethod
    def cover_url(key: KeyType, value: str | int | None, size: Size = "L") -> str | None:
        """
        https://openlibrary.org/dev/docs/api/covers
        """
        if value is None:
            return None

        return f"https://covers.openlibrary.org/b/{key}/{value}-{size}.jpg"


@dataclasses.dataclass()
class CachedOpenLibraryClient(OpenLibraryAPI):
    def author(self, id: str) -> Author:
        log = logger.bind(id=id)
        flask.g.setdefault("openlibrary_authors", {})

        if id not in flask.g.openlibrary_authors:
            flask.g.openlibrary_authors[id] = super().author(id)
            log.info("Populated author cache")
        else:
            log.info("Used author from cache")

        return flask.g.openlibrary_authors[id]
