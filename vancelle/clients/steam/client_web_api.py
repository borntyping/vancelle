import dataclasses
import typing

import structlog

from vancelle.clients.client import ApiClient

logger = structlog.get_logger(logger_name=__name__)


class ISteamApps_GetAppList_Apps_App(typing.TypedDict):
    appid: int
    name: str


class ISteamApps_GetAppList_Apps(typing.TypedDict):
    apps: list[ISteamApps_GetAppList_Apps_App]


class ISteamApps_GetAppList(typing.TypedDict):
    applist: ISteamApps_GetAppList_Apps


class SteamWebAPI(ApiClient):
    def ISteamApps_GetAppList(self) -> list[ISteamApps_GetAppList_Apps_App]:
        """
        https://steamapi.xpaw.me/#ISteamApps/GetAppList
        https://partner.steamgames.com/doc/webapi/ISteamApps#GetAppList

        Has returned some inconsistent results. Maybe use IStoreService instead?
        https://steamapi.xpaw.me/#IStoreService/GetAppList
        """
        logger.info("Fetching Steam appid list")

        url = f"https://api.steampowered.com/ISteamApps/GetAppList/v2/"
        response = self.get(url)
        response.raise_for_status()

        data: ISteamApps_GetAppList = response.json()
        apps = data["applist"]["apps"]

        logger.info("Fetched Steam appid list", count=len(apps))
        return apps
