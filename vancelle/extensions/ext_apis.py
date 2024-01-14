import dataclasses
import pathlib
import typing

import flask
import platformdirs
import requests_cache
import structlog

from ..clients.images.client import ImageCache
from ..clients.openlibrary.client import CachedOpenLibraryClient, OpenLibraryAPI
from ..clients.royalroad.client import RoyalRoadScraper
from ..clients.steam.client_store_api import SteamStoreAPI
from ..clients.steam.client_web_api import SteamWebAPI
from ..clients.tmdb.client import TmdbAPI

logger = structlog.get_logger(logger_name=__name__)


@dataclasses.dataclass(kw_only=True)
class ApisExtensionState:
    images: ImageCache
    openlibrary: OpenLibraryAPI
    royalroad: RoyalRoadScraper
    steam_store: SteamStoreAPI
    steam_web: SteamWebAPI
    tmdb: TmdbAPI


class ApisExtension:
    EXTENSION_NAME: typing.ClassVar[str] = "vancelle/clients"
    CACHE_PATH_KEY: typing.ClassVar[str] = "CACHE_PATH"

    def init_app(self, app: flask.Flask) -> None:
        default_cache_path = platformdirs.user_cache_path(appname=app.name, appauthor="borntyping").as_posix()
        app.config.setdefault(self.CACHE_PATH_KEY, default_cache_path)

        cache_path = pathlib.Path(app.config[self.CACHE_PATH_KEY])
        cache_path.mkdir(exist_ok=True)

        app.extensions[self.EXTENSION_NAME] = ApisExtensionState(
            images=ImageCache(
                session=self._session(cache_path, "images"),
            ),
            openlibrary=CachedOpenLibraryClient(
                session=self._session(cache_path, "openlibrary"),
            ),
            royalroad=RoyalRoadScraper(
                session=self._session(cache_path, "royalroad"),
            ),
            steam_store=SteamStoreAPI(
                session=self._session(cache_path, "steam_store"),
            ),
            steam_web=SteamWebAPI(
                session=self._session(cache_path, "steam_web"),
                api_key=app.config["STEAM_WEB_API_KEY"],
            ),
            tmdb=TmdbAPI.create(
                dedicated_session=self._session(cache_path, "tmdb"),
                token=app.config["TMDB_READ_ACCESS_TOKEN"],
            ),
        )
        app.logger.info(f"Request caches will be placed in {cache_path}")

    def _session(self, cache_path: pathlib.Path, name: str) -> requests_cache.CachedSession:
        cache_name = str(cache_path / f"{name}.db")
        return requests_cache.CachedSession(
            cache_name=cache_name,
            backend="sqlite",
            expire_after=requests_cache.NEVER_EXPIRE,
        )

    def _state(self) -> ApisExtensionState:
        return flask.current_app.extensions[self.EXTENSION_NAME]

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
