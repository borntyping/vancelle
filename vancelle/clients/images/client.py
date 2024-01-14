import dataclasses
import hashlib
import io
import pathlib

import flask
import requests_cache
import structlog
import urllib3.util

from vancelle.clients.client import RequestsClient

logger = structlog.get_logger(logger_name=__name__)


@dataclasses.dataclass()
class ImageCache(RequestsClient):
    def as_response(self, url: str) -> flask.Response:
        response = self.get(url)
        directives = requests_cache.CacheDirectives(response.headers)
        max_age = directives.max_age or 31536000
        etag = directives.etag or hashlib.md5(response.content).hexdigest()

        return flask.send_file(
            path_or_file=io.BytesIO(response.content),
            download_name=self.download_name(url),
            mimetype=response.headers["Content-Type"],
            max_age=max_age,
            etag=etag,
        )

    @staticmethod
    def download_name(url: str) -> str:
        """
        >>> ImageCache.download_name('http://example.invalid/cover.jpg')
        'cover.jpg'
        """
        return pathlib.Path(urllib3.util.parse_url(url).path).name
