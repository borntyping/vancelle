import pathlib
import typing

import bs4
import structlog

from vancelle.clients.client import RequestsClient
from vancelle.models import RoyalroadFiction

logger = structlog.get_logger(logger_name=__name__)


class RoyalRoadScraper(RequestsClient):
    def fiction(self, remote_id: str) -> RoyalroadFiction:
        response = self.get(f"https://www.royalroad.com/fiction/{remote_id}")
        soup = bs4.BeautifulSoup(response.text, features="html.parser")
        return RoyalroadFiction(
            id=remote_id,
            title=soup.select_one(".page-content-inner .fic-title h1").string,
            author=soup.select_one(".page-content-inner .fic-title h4 a").string,
            description=soup.select_one(".fiction-info .description p").string,
            cover=soup.select_one(".page-content-inner .cover-art-container img").attrs["src"],
        )

    def search_fictions(self, title: str) -> typing.Sequence[RoyalroadFiction]:
        response = self.get("https://www.royalroad.com/fictions/search", params={"title": title})
        soup = bs4.BeautifulSoup(response.text, features="html.parser")
        items = [
            RoyalroadFiction(
                id=pathlib.PurePath(tag.select_one("h2 a").attrs["href"]).parts[2],
                title=tag.select_one(".fiction-title a").string,
                description=tag.select_one("p").string,
                cover=tag.select_one("figure img").attrs["src"],
            )
            for tag in soup.select_one(".fiction-list").select(".fiction-list-item")
        ]
        logger.info("Searched Royal Road", title=title, count=len(items))
        return items
