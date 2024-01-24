import datetime
import json
import re
import typing

import structlog

from vancelle.clients.client import RequestsClient
from vancelle.clients.common import parse_date
from vancelle.models.remote import GoodreadsPublicBook

logger = structlog.get_logger(logger_name=__name__)

GoodreadsAggregateRatingSchema = typing.TypedDict(
    "GoodreadsAggregateRatingSchema",
    {
        "@type": typing.Literal["AggregateRating"],
        "ratingValue": float,
        "ratingCount": int,
        "reviewCount": int,
    },
)

GoodreadsPersonSchema = typing.TypedDict(
    "GoodreadsPersonSchema",
    {
        "@type": typing.Literal["Person"],
        "name": str,
        "url": str,
    },
)

GoodreadsBookSchema = typing.TypedDict(
    "GoodreadsBookSchema",
    {
        "@context": typing.Literal["https://schema.org"],
        "@type": typing.Literal["Book"],
        "name": str,
        "image": str,
        "bookFormat": str,
        "numberOfPages": int,
        "inLanguage": str,
        "isbn": str,
        "author": list[GoodreadsPersonSchema],
        "aggregateRating": GoodreadsAggregateRatingSchema,
    },
)


class GoodreadsPublicScraper(RequestsClient):
    def fetch(self, id: str) -> GoodreadsPublicBook:
        soup = self.soup(f"https://www.goodreads.com/book/show/{id}")

        page = soup.select_one(".BookPage")
        series = page.select_one(".BookPageTitleSection h3 a")
        scraped: dict[str, str] = {
            "series": series.get_text(" ") if series else None,
            "title": page.select_one(".BookPageTitleSection h1").string,
            "authors": [e.string for e in page.select_one(".ContributorLinksList").select('[data-testid="name"]')],
            "cover": page.select_one(".BookCover img").attrs["src"],
            "description": page.select_one('[data-testid="description"] span.Formatted').get_text("\n"),
            "genres": [
                e.string for e in page.select('[data-testid="genresList"] span.BookPageMetadataSection__genreButton span')
            ],
            "pagesFormat": page.select_one('[data-testid="pagesFormat"]').string,
            "publicationInfo": page.select_one(
                '[data-testid="publicationInfo"]'
            ).string,  ## crashes on missing data: https://www.goodreads.com/book/show/202985240
        }

        release_date = self.parse_date(scraped["publicationInfo"])
        data: GoodreadsBookSchema = json.loads(soup.select_one('script[type="application/ld+json"]').string)

        return GoodreadsPublicBook(
            id=id,
            title=scraped["title"],
            author=", ".join(scraped["authors"]),
            description=scraped["description"],
            release_date=release_date,
            cover=scraped["cover"],
            background=None,
            tags=set(scraped["genres"]),
            data={"scraped": scraped, "data": data},
        )

    def search(self, q: str) -> typing.Iterable[GoodreadsPublicBook]:
        soup = self.soup("https://www.goodreads.com/search", params={"q": q})
        for element in soup.select('[itemtype="http://schema.org/Book"]'):
            scraped: dict[str, str] = {
                "id": element.select_one(".u-anchorTarget").attrs["id"],
                "title": element.select_one('span[itemprop="name"]').string,
                "authors": [e.string for e in element.select('span[itemprop="author"] span[itemprop="name"]')],
                "cover": element.select_one("img.bookCover").attrs["src"],
            }
            published = self.parse_published(*element.select_one("span.uitext").stripped_strings)
            yield GoodreadsPublicBook(
                id=scraped["id"],
                title=scraped["title"],
                author=", ".join(scraped["authors"]),
                cover=scraped["cover"],
                release_date=published,
                data={"scraped": scraped, "data": {}},
            )

    RE_PUBLISHED = re.compile(r"published\s+(\d{4})")

    def parse_published(self, *strings: str) -> typing.Optional[datetime.date]:
        """
        >>> s = GoodreadsPublicScraper(...)
        >>> s.parse_published('3.61 avg rating — 223 ratings', '—\\n                published\\n               2013\\n              —', '4 editions')
        datetime.date(2013, 1, 1)
        >>> s.parse_published('4.58 avg rating — 701 ratings', '—', '2 editions') is None
        True
        """
        for string in strings:
            if match := self.RE_PUBLISHED.search(string):
                return datetime.date(year=int(match.group(1)), month=1, day=1)

        return None

    @staticmethod
    def parse_date(value: str) -> datetime.date:
        """
        >>> s = GoodreadsPublicScraper(...)
        >>> s.parse_date("First published September 15, 2022")
        datetime.date(2022, 9, 15)
        >>> s.parse_date("Expected publication June 18, 2024")
        datetime.date(2024, 6, 18)
        """
        return parse_date(
            value,
            [
                "First published %B %d, %Y",
                "Expected publication %B %d, %Y",
            ],
        )
