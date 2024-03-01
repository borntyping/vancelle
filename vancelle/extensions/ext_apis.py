import dataclasses
import pathlib
import sqlite3
import typing

import flask
import httpx
import platformdirs
import hishel
import structlog

from ..clients.goodreads.http import GoodreadsPublicScraper
from ..clients.images.client import ImageCache
from ..clients.openlibrary.client import CachedOpenLibraryClient, OpenLibraryAPI
from ..clients.royalroad.client import RoyalRoadScraper
from ..clients.steam.client_store_api import SteamStoreAPI
from ..clients.steam.client_web_api import SteamWebAPI
from ..clients.tmdb.client import TmdbAPI
from ..ext.httpx import BearerAuth

logger = structlog.get_logger(logger_name=__name__)


@dataclasses.dataclass(kw_only=True)
class Clients:
    goodreads: GoodreadsPublicScraper
    images: ImageCache
    openlibrary: OpenLibraryAPI
    royalroad: RoyalRoadScraper
    steam_store: SteamStoreAPI
    steam_web: SteamWebAPI
    tmdb: TmdbAPI


class ClientsExtension:
    EXTENSION_NAME: typing.ClassVar[str] = "vancelle/clients"
    CACHE_PATH_KEY: typing.ClassVar[str] = "CACHE_PATH"

    def init_app(self, app: flask.Flask) -> None:
        default_cache_path = platformdirs.user_cache_path(appname=app.name, appauthor="borntyping").as_posix()
        app.config.setdefault(self.CACHE_PATH_KEY, default_cache_path)

        directory = pathlib.Path(app.config[self.CACHE_PATH_KEY])
        directory.mkdir(exist_ok=True)
        app.logger.info(f"Outgoing requests will be cached in {directory}")

        app.extensions[self.EXTENSION_NAME] = Clients(
            goodreads=GoodreadsPublicScraper(
                client=hishel.CacheClient(
                    storage=hishel.FileStorage(
                        base_path=directory / "goodreads",
                    ),
                ),
            ),
            images=ImageCache(
                client=hishel.CacheClient(
                    follow_redirects=True,
                    storage=hishel.FileStorage(
                        base_path=directory / "images",
                    ),
                ),
            ),
            openlibrary=CachedOpenLibraryClient(
                client=hishel.CacheClient(
                    storage=hishel.SQLiteStorage(
                        connection=sqlite3.connect(directory / "openlibrary.sqlite"),
                    ),
                ),
            ),
            royalroad=RoyalRoadScraper(
                client=hishel.CacheClient(
                    storage=hishel.SQLiteStorage(
                        connection=sqlite3.connect(directory / "royalroad.sqlite"),
                    ),
                ),
            ),
            steam_store=SteamStoreAPI(
                client=hishel.CacheClient(
                    storage=hishel.SQLiteStorage(
                        connection=sqlite3.connect(directory / "steam_store.sqlite"),
                    ),
                ),
            ),
            steam_web=SteamWebAPI(
                client=hishel.CacheClient(
                    storage=hishel.SQLiteStorage(
                        connection=sqlite3.connect(directory / "steam_web.sqlite"),
                    ),
                    headers={"key": app.config["STEAM_WEB_API_KEY"]},
                ),
            ),
            tmdb=TmdbAPI(
                client=hishel.CacheClient(
                    storage=hishel.SQLiteStorage(
                        connection=sqlite3.connect(directory / "tmdb.sqlite"),
                    ),
                    auth=BearerAuth(app.config["TMDB_READ_ACCESS_TOKEN"]),
                ),
            ),
        )

    def _client(
        self,
        cache_path: pathlib.Path,
        auth: httpx.Auth | None = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> hishel.CacheClient:
        return hishel.CacheClient(
            auth=auth,
            params=params,
            headers=headers,
            controller=hishel.Controller(
                allow_stale=True,
            ),
            storage=hishel.SQLiteStorage(
                connection=sqlite3.connect(cache_path),
            ),
        )

    def _state(self) -> Clients:
        return flask.current_app.extensions[self.EXTENSION_NAME]

    @property
    def goodreads(self) -> GoodreadsPublicScraper:
        return self._state().goodreads

    @property
    def images(self) -> ImageCache:
        return self._state().images

    @property
    def openlibrary(self) -> OpenLibraryAPI:
        return self._state().openlibrary

    @property
    def royalroad(self) -> RoyalRoadScraper:
        return self._state().royalroad

    @property
    def steam_store_api(self) -> SteamStoreAPI:
        return self._state().steam_store

    @property
    def steam_web_api(self) -> SteamWebAPI:
        return self._state().steam_web

    @property
    def tmdb(self) -> TmdbAPI:
        return self._state().tmdb
