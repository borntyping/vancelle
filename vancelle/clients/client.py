import dataclasses
import typing

import requests_cache
import structlog

logger = structlog.get_logger(logger_name=__name__)


@dataclasses.dataclass()
class RequestsClient:
    session: requests_cache.CachedSession

    def get(self, url: str, **kwargs: typing.Any) -> requests_cache.AnyResponse:
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        logger.info(
            "Finished request",
            url=response.url,
            status_code=response.status_code,
            from_cache=response.from_cache,
        )
        return response
