import datetime
import json
import typing

from vancelle.clients.client import RequestsClient
from vancelle.models.remote import GoodreadsPublicBook

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
        scraped: dict[str, str] = {
            "series": page.select_one(".BookPageTitleSection h3 a").get_text(" "),
            "title": page.select_one(".BookPageTitleSection h1").string,
            "authors": [e.string for e in page.select_one(".ContributorLinksList").select('[data-testid="name"]')],
            "description": page.select_one('[data-testid="description"] span.Formatted').get_text("\n"),
            "genres": [
                e.string for e in page.select('[data-testid="genresList"] span.BookPageMetadataSection__genreButton span')
            ],
            "pagesFormat": page.select_one('[data-testid="pagesFormat"]').string,
            "publicationInfo": page.select_one('[data-testid="publicationInfo"]').string,
        }

        release_date = self.parse_date(scraped["publicationInfo"])
        cover = page.select_one(".BookCover img").attrs["src"]

        data: GoodreadsBookSchema = json.loads(soup.select_one('script[type="application/ld+json"]').string)
        return GoodreadsPublicBook(
            id=id,
            title=scraped["title"],
            author=", ".join(scraped["authors"]),
            description=scraped["description"],
            release_date=release_date,
            cover=cover,
            background=None,
            tags=set(scraped["genres"]),
            data={"scraped": scraped, "data": data},
        )

    def search(self, q: str) -> typing.Sequence[GoodreadsPublicBook]:
        soup = self.soup("https://www.goodreads.com/search", params={"q": q})
        return [
            GoodreadsPublicBook(
                id=element.select_one(".u-anchorTarget").attrs["id"],
                title=element.select_one('span[itemprop="name"]').string,
                author=element.select_one('span[itemprop="author"]').string,
                cover=element.select_one("img.bookCover").attrs["src"],
            )
            for element in soup.select('[itemtype="http://schema.org/Book"]')
        ]

    @staticmethod
    def parse_date(value: str) -> datetime.date:
        """
        >>> GoodreadsPublicScraper(...).parse_date("First published September 15, 2022")
        datetime.date(2022, 9, 15)
        >>> GoodreadsPublicScraper(...).parse_date("First published January 1, 1900")
        datetime.date(1900, 1, 1)
        """
        return datetime.datetime.strptime(value, "First published %B %d, %Y").date()
