import dataclasses
import datetime
import typing

import requests_cache
import structlog

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


@dataclasses.dataclass()
class SteamStoreAPI:
    session: requests_cache.CachedSession

    def appdetails(self, appid: str) -> AppDetails | None:
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
        response = self.session.get(url)
        response.raise_for_status()
        data: AppDetailsContainer = response.json()

        wrapper = data[appid]
        if not wrapper["success"]:
            logger.warning(f"Steam appdetails request failed", appid=appid, data=data)
            return None

        logger.info(
            "Fetched appdetails from Steam store",
            appid=appid,
            url=response.url,
            status_code=response.status_code,
            from_cache=response.from_cache,
        )
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
            response = self.session.get(url)
            logger.debug(
                "Fetched Steam vertical capsule image",
                appid=appid,
                url=response.request.url,
                status_code=response.status_code,
                from_cache=response.from_cache,
            )
            if not response.ok:
                return None

        return url

    @staticmethod
    def parse_release_date(release_date: AppDetailsReleaseDate) -> datetime.date | None:
        if release_date["coming_soon"]:
            return None

        try:
            return datetime.datetime.strptime(release_date["date"], "%d %b, %Y").date()
        except ValueError:
            return None
