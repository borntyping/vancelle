import dataclasses

import flask
import platformdirs
import requests_cache
import structlog

from ..clients.openlibrary.client import CachedOpenLibraryClient, OpenLibraryAPI
from ..clients.royalroad.client import RoyalRoadScraper
from ..clients.steam.client_store_api import SteamStoreAPI
from ..clients.steam.client_web_api import SteamWebAPI
from ..clients.tmdb.client import TmdbAPI

logger = structlog.get_logger(logger_name=__name__)


@dataclasses.dataclass(kw_only=True)
class ApisExtensionState:
    openlibrary: OpenLibraryAPI
    royalroad: RoyalRoadScraper
    steam_store: SteamStoreAPI
    steam_web: SteamWebAPI
    tmdb: TmdbAPI


@dataclasses.dataclass(kw_only=True)
class ApisExtension:
    def init_app(self, app: flask.Flask) -> None:
        user_cache_path = platformdirs.user_cache_path(appname=app.name, appauthor="borntyping", ensure_exists=True)
        app.config.setdefault("APIS_REQUEST_CACHE_NAME", str(user_cache_path / "requests_cache.db"))

        shared_session = self._create_requests_session(app)
        app.extensions["vancelle/clients"] = ApisExtensionState(
            openlibrary=CachedOpenLibraryClient(session=shared_session),
            royalroad=RoyalRoadScraper(session=shared_session),
            steam_web=SteamWebAPI(session=shared_session, api_key=app.config["STEAM_WEB_API_KEY"]),
            steam_store=SteamStoreAPI(session=shared_session),
            tmdb=TmdbAPI.create(
                dedicated_session=self._create_requests_session(app),
                token=app.config["TMDB_READ_ACCESS_TOKEN"],
            ),
        )

    def _create_requests_session(self, app: flask.Flask) -> requests_cache.CachedSession:
        return requests_cache.CachedSession(
            cache_name=app.config["APIS_REQUEST_CACHE_NAME"],
            backend="sqlite",
            expire_after=requests_cache.NEVER_EXPIRE,
        )

    def _state(self) -> ApisExtensionState:
        return flask.current_app.extensions["vancelle/clients"]

    @property
    def openlibrary(self) -> OpenLibraryAPI:
        return self._state().openlibrary

    @property
    def royalroad(self) -> RoyalRoadScraper:
        return self._state().royalroad

    @property
    def steam_web_api(self) -> SteamWebAPI:
        return self._state().steam_web

    @property
    def steam_store_api(self) -> SteamStoreAPI:
        return self._state().steam_store

    @property
    def tmdb(self) -> TmdbAPI:
        return self._state().tmdb
