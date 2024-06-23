from datetime import date, datetime
from typing import Literal, Optional
from uuid import UUID

import pydantic
import sqlalchemy
import structlog

from vancelle.controllers.sources.steam import SteamApplicationSource
from vancelle.extensions import db
from vancelle.models import Record, Remote, User
from ..models.work import Work
from ..shelf import Shelf

logger = structlog.get_logger(logger_name=__name__)


class RemoteModel(pydantic.BaseModel):
    work_id: UUID
    type: str
    id: str

    time_created: datetime
    time_updated: Optional[datetime]
    time_deleted: Optional[datetime]

    title: Optional[str]
    author: Optional[str]
    description: Optional[str]
    release_date: Optional[date]
    cover: Optional[str]
    background: Optional[str]
    shelf: Optional[Shelf]
    tags: Optional[set[str]]
    data: Optional[pydantic.JsonValue]


class RecordModel(pydantic.BaseModel):
    work_id: UUID
    id: UUID

    time_created: datetime
    time_updated: Optional[datetime]
    time_deleted: Optional[datetime]

    date_started: Optional[date]
    date_stopped: Optional[date]
    notes: Optional[str]


class WorkModel(pydantic.BaseModel):
    id: UUID
    type: str

    time_created: datetime
    time_updated: Optional[datetime]
    time_deleted: Optional[datetime]

    title: Optional[str]
    author: Optional[str]
    description: Optional[str]
    release_date: Optional[date]
    cover: Optional[str]
    background: Optional[str]
    shelf: Optional[Shelf]
    tags: Optional[set[str]]

    remotes: list[RemoteModel]
    records: list[RecordModel]


class BackupModel(pydantic.BaseModel):
    version: Literal[2]
    works: list[WorkModel]


class UserSettingsController:
    def export_json(self, user: User) -> str:
        works = (
            db.session.execute(sqlalchemy.select(Work).filter_by(user_id=user.id).options(sqlalchemy.orm.selectinload("*")))
            .scalars()
            .all()
        )

        backup = BackupModel(
            version=2,
            works=pydantic.TypeAdapter(list[WorkModel]).validate_python(works, from_attributes=True),
        )

        logger.warning("Exported", user=user.id, works=len(backup.works))
        return backup.model_dump_json(indent=2)

    def import_json(self, json_data: str, user: User, dry_run: bool = False):
        backup = BackupModel.model_validate_json(json_data=json_data)

        works = [
            Work(
                **work.model_dump(exclude_unset=True, exclude={"records", "remotes"}),
                records=[Record(**r.model_dump(exclude_unset=True)) for r in work.records],
                remotes=[Remote(**r.model_dump(exclude_unset=True)) for r in work.remotes],
            )
            for work in backup.works
        ]

        for work in works:
            work.user = user

        if not dry_run:
            db.session.add_all(works)
            db.session.commit()

        logger.warning("Imported", user=user.id, works=len(works))


class ApplicationSettingsController:
    def reload_steam_cache(self) -> None:
        SteamApplicationSource.reload_appid_cache()
