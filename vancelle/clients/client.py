import dataclasses
import typing

import bs4
import requests
import requests_cache
import structlog

logger = structlog.get_logger(logger_name=__name__)


@dataclasses.dataclass()
class RequestsClient:
    session: requests_cache.CachedSession

    def get(self, url: str, **kwargs: typing.Any) -> requests_cache.AnyResponse:
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        logger.debug(
            "Finished request",
            url=response.url,
            status_code=response.status_code,
            elapsed=response.elapsed,
            from_cache=getattr(response, "from_cache", None),
            expires_delta=getattr(response, "expires_delta", None),
        )
        return response

    def soup(self, url: str, **kwargs: typing.Any) -> bs4.BeautifulSoup:
        return self.request_into_soup(self.get(url, **kwargs))

    def request_into_soup(self, response: requests.Response) -> bs4.BeautifulSoup:
        return bs4.BeautifulSoup(response.text, features="html.parser")
