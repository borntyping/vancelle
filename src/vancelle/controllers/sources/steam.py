import structlog
import svcs
from sqlalchemy import desc, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Mapped, mapped_column

from .base import Source
from ...clients.steam.client_store_api import SteamStoreAPI
from ...clients.steam.client_web_api import SteamWebAPI
from ...lib.pagination import Pagination
from ...extensions import db
from ...inflect import p
from ...lib.pagination.flask import FlaskPaginationArgs
from ...models import Base
from ...models.remote import SteamApplication
from ...models.work import Game

logger = structlog.get_logger(logger_name=__name__)


class SteamAppID(Base):
    __tablename__ = "steam_appids"

    appid: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class SteamApplicationSource(Source):
    remote_type = SteamApplication
    work_type = Game

    def fetch(self, remote_id: str) -> SteamApplication:
        api = svcs.flask.get(SteamStoreAPI)

        appdetails = api.appdetails(remote_id)

        if appdetails is None:
            return SteamApplication(id=remote_id, data={})

        release_date = api.parse_release_date(appdetails["release_date"])
        vertical_capsule = api.vertical_capsule(appdetails, check=True)
        author = p.join(appdetails["developers"] if appdetails["developers"] else [])

        return SteamApplication(
            id=str(appdetails["steam_appid"]),
            title=appdetails["name"],
            author=author,
            description=appdetails["short_description"],
            release_date=release_date,
            cover=vertical_capsule,
            background=appdetails["background"],
            data=appdetails,
        )

    def search(self, query: str) -> Pagination:
        pagination_args = FlaskPaginationArgs()

        log = logger.bind(query=query)
        log.info("Searching Steam apps")

        if not query:
            return Pagination.empty()

        self.ensure_appid_cache()

        stmt = (
            select(SteamAppID)
            .filter(SteamAppID.name.ilike(f"%{query}%"))
            .order_by(
                desc(SteamAppID.name == query),
                desc(SteamAppID.name.ilike(f"%{query}%")),
                desc(SteamAppID.appid),
            )
        )

        pagination = pagination_args.query(db.session, stmt)
        return pagination.map(lambda a: SteamApplication(id=a.appid, title=a.name))

    def ensure_appid_cache(self) -> None:
        appid_count = db.session.execute(select(func.count()).select_from(SteamAppID).limit(1)).scalar_one()
        if appid_count == 0:
            self.reload_appid_cache()

    @staticmethod
    def reload_appid_cache() -> None:
        logger.warning("Reloading Steam application cache")
        api = svcs.flask.get(SteamWebAPI)
        apps = api.ISteamApps_GetAppList()

        logger.debug("Inserting Steam appid cache")
        stmt = insert(SteamAppID)
        stmt = stmt.on_conflict_do_update(index_elements=[SteamAppID.appid], set_={"name": stmt.excluded.name})
        db.session.execute(stmt, apps)
        db.session.commit()

        logger.warning("Recreated Steam appid cache", count=len(apps))
