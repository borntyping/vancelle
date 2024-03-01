import structlog

from vancelle.controllers.sources.steam import SteamApplicationManager

logger = structlog.get_logger(logger_name=__name__)


class CacheController:
    def reload_steam_cache(self) -> None:
        SteamApplicationManager.reload_appid_cache()
