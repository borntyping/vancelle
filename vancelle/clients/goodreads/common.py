import dataclasses
import datetime
import hashlib
import pathlib
import typing
import uuid

import structlog
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified

from vancelle.models import GoodreadsBook, Record, User, Work
from vancelle.extensions import db
from vancelle.types import Shelf, WorkType

logger = structlog.get_logger(logger_name=__name__)


@dataclasses.dataclass(frozen=True)
class GoodreadsImporter:
    shelf_mapping: typing.Dict[str, Shelf]
    user: User

    def reproducible_uuid(self, value: str) -> uuid.UUID:
        return uuid.UUID(hashlib.md5(value.encode("utf-8")).hexdigest())

    def parse_shelf(self, exclusive_shelf: str, date_published: datetime.date) -> Shelf:
        if date_published and date_published > datetime.date.today():
            return Shelf.UNRELEASED

        return self.shelf_mapping[exclusive_shelf]

    def load_file(self, path: pathlib.Path) -> typing.Iterable[Work | GoodreadsBook]:
        raise NotImplementedError

    def load_stream(self, stream: typing.IO[bytes], *, filename: str) -> typing.Iterable[Work | GoodreadsBook]:
        raise NotImplementedError

    def add_items(self, items: typing.Sequence[Work | GoodreadsBook]) -> None:
        db.session.add_all(items)
        db.session.commit()
        logger.warning("Imported books from Goodreads", count=len(items))

    def get_remote(self, remote_id: str) -> GoodreadsBook | None:
        return db.session.execute(select(GoodreadsBook).filter_by(id=remote_id)).scalar_one_or_none()

    def get_record(self, record_id: uuid.UUID) -> Record | None:
        return db.session.get(Record, record_id)

    def _create_or_update(
        self,
        *,
        remote_id: str,
        title: str,
        author: str,
        release_date: datetime.date,
        cover: str = None,
        shelf: Shelf,
        tags: list[str] = None,
        date_started: datetime.date = None,
        date_stopped: datetime.date,
        isbn13: str,
        data: typing.Mapping[str, typing.Any],
    ):
        log = logger.bind(remote_id=remote_id, title=title, author=author)
        if remote := self.get_remote(remote_id):
            log.info("Updating existing Goodreads book")
        else:
            log.info("Creating new Goodreads book")
            remote = GoodreadsBook(id=remote_id)

        if title:
            remote.title = title
        if author:
            remote.author = author
        if release_date:
            remote.release_date = release_date
        if cover:
            remote.cover = cover
        if shelf:
            remote.shelf = shelf
        if tags:
            remote.tags = tags

        if remote.data is None:
            remote.data = {}

        remote.data.update(data)
        flag_modified(remote, "data")

        if isbn13:
            remote.data["isbn13"] = isbn13
            flag_modified(remote, "data")

        if not remote.work:
            work_id = self.reproducible_uuid(remote_id)
            remote.work = Work(user_id=self.user.id, id=work_id, type=WorkType.BOOK)

        if date_started or date_stopped:
            record_id = self.reproducible_uuid(remote_id)
            record = self.get_record(record_id) or Record(id=record_id)
            if date_started:
                record.date_started = date_started
            if date_stopped:
                record.date_stopped = date_stopped
            remote.work.records.append(record)

        return remote
