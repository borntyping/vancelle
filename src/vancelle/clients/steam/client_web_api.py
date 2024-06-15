import typing

import flask
import hishel
import structlog
import svcs

from vancelle.clients.client import HttpClient, HttpClientBuilder

logger = structlog.get_logger(logger_name=__name__)


class ISteamApps_GetAppList_Apps_App(typing.TypedDict):
    appid: int
    name: str


class ISteamApps_GetAppList_Apps(typing.TypedDict):
    apps: list[ISteamApps_GetAppList_Apps_App]


class ISteamApps_GetAppList(typing.TypedDict):
    applist: ISteamApps_GetAppList_Apps


class SteamWebAPI(HttpClient):
    @classmethod
    def factory(cls, svcs_container: svcs.Container) -> typing.Self:
        app, builder = svcs_container.get(flask.Flask, HttpClientBuilder)
        return cls(
            client=hishel.CacheClient(
                storage=builder.sqlite_storage_for(cls),
                headers={"key": app.config["STEAM_WEB_API_KEY"]},
            ),
        )

    def ISteamApps_GetAppList(self) -> list[ISteamApps_GetAppList_Apps_App]:
        """
        https://steamapi.xpaw.me/#ISteamApps/GetAppList
        https://partner.steamgames.com/doc/webapi/ISteamApps#GetAppList

        Has returned some inconsistent results. Maybe use IStoreService instead?
        https://steamapi.xpaw.me/#IStoreService/GetAppList
        """
        logger.info("Fetching Steam appid list")

        url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
        response = self.get(url)
        response.raise_for_status()

        data: ISteamApps_GetAppList = response.json()
        apps = data["applist"]["apps"]

        logger.info("Fetched Steam appid list", count=len(apps))
        return apps
