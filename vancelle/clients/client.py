import dataclasses
import typing

import bs4
import hishel
import httpx
import structlog

logger = structlog.get_logger(logger_name=__name__)


@dataclasses.dataclass()
class ApiClient:
    client: hishel.CacheClient

    def get(
        self,
        url: str,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        response = self.client.get(url, params=params, headers=headers)
        self._debug(response)
        response.raise_for_status()
        return response

    def head(self, url: str) -> httpx.Response:
        response = self.client.head(url)
        self._debug(response)
        response.raise_for_status()
        return response

    def _debug(self, response: httpx.Response):
        logger.debug(
            "Finished request",
            url=str(response.url),
            status_code=response.status_code,
            elapsed=response.elapsed.total_seconds(),
            from_cache=response.extensions["from_cache"],
            cache_metadata=response.extensions.get("cache_metadata"),
        )

    def soup(self, url: str, **kwargs: typing.Any) -> bs4.BeautifulSoup:
        return self.request_into_soup(self.get(url, **kwargs))

    def request_into_soup(self, response: httpx.Response) -> bs4.BeautifulSoup:
        return bs4.BeautifulSoup(response.text, features="html.parser")
