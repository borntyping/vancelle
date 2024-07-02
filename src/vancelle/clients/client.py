import dataclasses
import pathlib
import sqlite3
import typing

import bs4
import flask
import hishel
import httpx
import platformdirs
import structlog
import svcs

logger = structlog.get_logger(logger_name=__name__)


@dataclasses.dataclass
class HttpClientBuilder:
    cache_directory: pathlib.Path

    @classmethod
    def factory(cls, svcs_container: svcs.Container) -> typing.Self:
        app = svcs_container.get(flask.Flask)
        key = "CACHE_PATH"

        default = platformdirs.user_cache_path(appname=app.name, appauthor="borntyping").as_posix()
        app.config.setdefault(key, default)

        path = pathlib.Path(app.config[key])
        path.mkdir(exist_ok=True)
        app.logger.info(f"Outgoing requests will be cached in {path}")

        return cls(path)

    def sqlite_storage_for(self, cls: typing.Type) -> hishel.SQLiteStorage:
        connection = sqlite3.connect(self.cache_directory / f"{cls.__name__}.sqlite")
        return hishel.SQLiteStorage(connection=connection)

    def filesystem_storage_for(self, cls: typing.Type) -> hishel.FileStorage:
        return hishel.FileStorage(base_path=self.cache_directory / cls.__name__)


@dataclasses.dataclass()
class HttpClient:
    client: hishel.CacheClient

    def get(
        self,
        url: str,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        response = self.client.get(url, params=params, headers=headers, follow_redirects=True)
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
