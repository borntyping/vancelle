import structlog
from flask_sqlalchemy.pagination import Pagination
from sqlalchemy import desc, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Mapped, mapped_column

from .base import Manager
from ...ext.flask_sqlalchemy import EmptyPagination, SelectAndTransformPagination
from ...extensions import apis, db
from ...inflect import p
from ...models import Base
from ...models.remote import SteamApplication

logger = structlog.get_logger(logger_name=__name__)


class SteamAppID(Base):
    __tablename__ = "steam_appids"

    appid: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class SteamApplicationManager(Manager):
    remote_type = SteamApplication

    def fetch(self, remote_id: str) -> SteamApplication:
        appdetails = apis.steam_store_api.appdetails(remote_id)

        if appdetails is None:
            return SteamApplication(id=remote_id, data={})

        release_date = apis.steam_store_api.parse_release_date(appdetails["release_date"])
        vertical_capsule = apis.steam_store_api.vertical_capsule(appdetails, check=True)
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
        log = logger.bind(query=query)
        log.info("Searching Steam apps")

        if not query:
            return EmptyPagination()

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

        return SelectAndTransformPagination(
            select=stmt,
            session=db.session(),
            transform=lambda a: SteamApplication(id=a.appid, title=a.name),
        )

    def ensure_appid_cache(self) -> None:
        appid_count = db.session.execute(select(func.count()).select_from(SteamAppID).limit(1)).scalar_one()
        if appid_count == 0:
            self.reload_appid_cache()

    def reload_appid_cache(self) -> None:
        logger.warning("Reloading Steam application cache")
        apps = apis.steam_web_api.ISteamApps_GetAppList()

        logger.debug("Inserting Steam appid cache")

        stmt = insert(SteamAppID)
        stmt = stmt.on_conflict_do_update(index_elements=[SteamAppID.appid], set_={"name": stmt.excluded.name})

        db.session.execute(stmt, apps)
        db.session.commit()

        logger.warning("Recreated Steam appid cache", count=len(apps))
