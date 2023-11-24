import dataclasses
import typing

import requests_cache
import structlog

P = typing.ParamSpec("P")
logger = structlog.get_logger(logger_name=__name__)


@dataclasses.dataclass()
class RequestsClient:
    session: requests_cache.CachedSession

    def get(self, url: str, **kwargs: P.kwargs) -> requests_cache.CachedResponse:
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        logger.info(
            "Finished request",
            url=response.url,
            status_code=response.status_code,
            from_cache=response.from_cache,
        )
        return response
