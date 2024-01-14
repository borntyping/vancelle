import dataclasses
import io

import flask
import requests_cache
import structlog

logger = structlog.get_logger(logger_name=__name__)


@dataclasses.dataclass()
class ImageCache:
    session: requests_cache.CachedSession

    def as_response(self, url: str) -> flask.Response:
        response = self.session.get(url)
        response.raise_for_status()
        logger.debug("Fetched image", url=response.request.url, from_cache=response.from_cache)
        return flask.send_file(
            path_or_file=io.BytesIO(response.content),
            mimetype=response.headers["Content-Type"],
        )
