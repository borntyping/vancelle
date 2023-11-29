import typing
import uuid
from datetime import date, datetime
from typing import Literal, Optional
from uuid import UUID

import pydantic
import sqlalchemy
import structlog

from vancelle.extensions import db
from vancelle.models import Base, User
from ..models.remote import Remote
from ..models.record import Record
from ..models.work import Work
from ..shelf import Shelf

logger = structlog.get_logger(logger_name=__name__)
S = typing.TypeVar("S", bound=Base)
P = typing.TypeVar("P", bound="DataModel")


class DataModel(pydantic.BaseModel):
    pass


class UserModel(DataModel):
    id: uuid.UUID
    username: str
    password: str


class WorkModel(DataModel):
    user_id: uuid.UUID
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


class RemoteModel(DataModel):
    work_id: uuid.UUID
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


class RecordModel(DataModel):
    work_id: uuid.UUID
    id: UUID

    time_created: datetime
    time_updated: Optional[datetime]
    time_deleted: Optional[datetime]

    date_started: Optional[date]
    date_stopped: Optional[date]
    notes: Optional[str]


class ExportModel(DataModel):
    version: Literal[1] = 1

    users: list[UserModel]
    works: list[WorkModel]
    records: list[RecordModel]
    remotes: list[RemoteModel]


class DataController:
    def export_json(self) -> str:
        data = ExportModel(
            users=self._export_model(User, UserModel),
            works=self._export_model(Work, WorkModel),
            records=self._export_model(Record, RecordModel),
            remotes=self._export_model(Remote, RemoteModel),
        )

        logger.warning(
            "Exported",
            users=len(data.users),
            works=len(data.works),
            records=len(data.records),
            remotes=len(data.remotes),
        )

        return data.model_dump_json(indent=2)

    def _export_model(self, orm_model: typing.Type[S], pydantic_model: typing.Type[P]) -> list[P]:
        items = db.session.execute(sqlalchemy.select(orm_model).options(sqlalchemy.orm.raiseload("*"))).scalars().all()
        return pydantic.TypeAdapter(list[pydantic_model]).validate_python(items, from_attributes=True)

    def import_json(self, json_data: str, filename: str, dry_run: bool = True):
        data = ExportModel.model_validate_json(json_data=json_data)

        users = self._import_model(User, data.users)
        works = self._import_model(Work, data.works)
        records = self._import_model(Record, data.records)
        remotes = self._import_model(Remote, data.remotes)

        if not dry_run:
            db.session.add_all(users)
            db.session.add_all(works)
            db.session.add_all(records)
            db.session.add_all(remotes)
            db.session.commit()

        logger.warning(
            "Imported",
            users=len(users),
            works=len(works),
            records=len(records),
            remotes=len(remotes),
            filename=filename,
        )

    def _import_model(self, orm_model: typing.Type[S], pydantic_items: list[P]) -> list[S]:
        return [orm_model(**item.model_dump(exclude_unset=True)) for item in pydantic_items]
