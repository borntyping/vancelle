import hashlib
import pathlib
import typing

import flask
import hishel
import httpx
import structlog
import svcs

from vancelle.clients.client import HttpClient, HttpClientBuilder

logger = structlog.get_logger(logger_name=__name__)


class ImageCache(HttpClient):
    @classmethod
    def factory(cls, svcs_container: svcs.Container) -> typing.Self:
        app, builder = svcs_container.get(flask.Flask, HttpClientBuilder)
        return cls(client=hishel.CacheClient(storage=builder.filesystem_storage_for(cls)))

    def as_response(self, url: str) -> flask.Response:
        response = self.get(url)

        headers = dict()
        headers["Content-Disposition"] = f'attachment; filename="{self.filename(response.url)}"'

        for header in ["Content-Type", "Last-Modified"]:
            if last_modified := response.headers.get(header):
                headers[header] = last_modified

        if "ETag" not in response.headers:
            headers["ETag"] = hashlib.md5(response.content).hexdigest()

        return flask.Response(response=response.content, headers=headers)

    @staticmethod
    def filename(url: httpx.URL) -> str:
        """
        >>> ImageCache.filename(httpx.URL('http://example.invalid/cover.jpg'))
        'cover.jpg'
        """
        return pathlib.Path(url.path).name
