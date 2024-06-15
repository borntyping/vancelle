import datetime
import typing

import hishel
import httpx
import structlog
import svcs

from ..client import HttpClient, HttpClientBuilder
from ..common import parse_date

logger = structlog.get_logger(logger_name=__name__)


class AppDetailsReleaseDate(typing.TypedDict):
    coming_soon: bool
    date: str


class AppDetailsFullGame(typing.TypedDict):
    appid: str
    name: str


class AppDetails(typing.TypedDict):
    type: str
    name: str
    steam_appid: int
    dlc: list[int]

    """
    Header capsule. 460px x 215px.
    https://partner.steamgames.com/doc/store/assets/standard#header_capsule
    """
    header_image: str

    """
    Small capsule. 231px x 87px.
    https://partner.steamgames.com/doc/store/assets/standard#small_capsule
    """
    capsule_image: str

    """
    Downscaled small capsule. 184px x 69px.
    https://partner.steamgames.com/doc/store/assets/standard#small_capsule
    """
    capsule_imagev5: str
    background: str
    background_raw: str
    release_date: AppDetailsReleaseDate
    developers: list[str]
    publishers: list[str]

    fullgame: typing.NotRequired[AppDetailsFullGame]
    short_description: str


class AppDetailsWrapper(typing.TypedDict):
    success: bool
    data: AppDetails


AppDetailsContainer = typing.NewType("AppDetailsContainer", dict[str, AppDetailsWrapper])


class SteamStoreAPI(HttpClient):
    @classmethod
    def factory(cls, svcs_container: svcs.Container) -> typing.Self:
        builder = svcs_container.get(HttpClientBuilder)
        return cls(client=hishel.CacheClient(storage=builder.sqlite_storage_for(cls)))

    def appdetails(self, appid: str) -> AppDetails | None:
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
        response = self.get(url)
        response.raise_for_status()
        data: AppDetailsContainer = response.json()

        wrapper = data[appid]
        if not wrapper["success"]:
            logger.warning(f"Steam appdetails request failed", appid=appid, data=data)
            return None

        return wrapper["data"]

    def vertical_capsule(self, app: AppDetails, check: bool = True) -> str | None:
        """
        Vertical Capsule. 374px x 448px. Should look like box art.
        Not in the appdetails API.
        https://partner.steamgames.com/doc/store/assets/standard#vertical_capsule
        """
        if "fullgame" in app:
            appid = app["fullgame"]["appid"]
        else:
            appid = str(app["steam_appid"])

        url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/library_600x900_2x.jpg"

        if check:
            try:
                self.head(url)
            except httpx.HTTPStatusError:
                return None

        return url

    @staticmethod
    def parse_release_date(release_date: AppDetailsReleaseDate) -> datetime.date | None:
        """
        >>> SteamStoreAPI(...).parse_release_date({"coming_soon": True, "date": "Coming soon"}) is None
        True
        >>> SteamStoreAPI(...).parse_release_date({"coming_soon": True, "date": "13 Feb, 2024"})
        datetime.date(2024, 2, 13)
        >>> SteamStoreAPI(...).parse_release_date({"coming_soon": False, "date": "20 Jan, 2021"})
        datetime.date(2021, 1, 20)
        """
        if release_date["date"] == "Coming soon":
            return None

        return parse_date(release_date["date"], ["%d %b, %Y"])
