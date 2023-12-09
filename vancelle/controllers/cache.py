import requests
import requests_cache
import structlog

from vancelle.controllers.sources.steam import SteamApplicationManager

logger = structlog.get_logger(logger_name=__name__)


class CacheController:
    def clear_request_cache(self) -> None:
        session = requests.Session()
        if isinstance(session, requests_cache.CachedSession):
            logger.warning("Clearing requests cache")
            session.cache.clear()

    def reload_steam_cache(self) -> None:
        SteamApplicationManager.reload_appid_cache()
