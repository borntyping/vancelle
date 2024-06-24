import dataclasses
import datetime
import hashlib
import pathlib
import typing
import uuid

import structlog
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified

from vancelle.models import User
from vancelle.models.entry import GoodreadsPrivateBook
from vancelle.models.record import Record
from vancelle.models.work import Book
from vancelle.extensions import db
from vancelle.shelf import Shelf

logger = structlog.get_logger(logger_name=__name__)


@dataclasses.dataclass(frozen=True)
class GoodreadsImporter:
    shelf_mapping: typing.Dict[str, Shelf]
    user: User

    def reproducible_uuid(self, value: str) -> uuid.UUID:
        return uuid.UUID(hashlib.md5(value.encode("utf-8")).hexdigest())

    def parse_shelf(self, exclusive_shelf: str | None, date_published: datetime.date | None) -> Shelf:
        if not exclusive_shelf:
            raise ValueError("Missing shelf")

        if date_published and date_published > datetime.date.today():
            return Shelf.UNRELEASED

        return self.shelf_mapping[exclusive_shelf]

    def load_file(self, path: pathlib.Path) -> typing.Iterable[Book | GoodreadsPrivateBook]:
        raise NotImplementedError

    def load_stream(self, stream: typing.IO[bytes], *, filename: str) -> typing.Iterable[Book | GoodreadsPrivateBook]:
        raise NotImplementedError

    def add_items(self, items: typing.Sequence[Book | GoodreadsPrivateBook]) -> None:
        db.session.add_all(items)
        db.session.commit()
        logger.warning("Imported books from Goodreads", count=len(items))

    def get_entry(self, entry_id: str) -> GoodreadsPrivateBook | None:
        return db.session.execute(select(GoodreadsPrivateBook).filter_by(id=entry_id)).scalar_one_or_none()

    def get_record(self, record_id: uuid.UUID) -> Record | None:
        return db.session.get(Record, record_id)

    def _create_or_update(
        self,
        *,
        entry_id: str,
        title: str,
        author: str,
        release_date: datetime.date | None,
        cover: str | None,
        shelf: Shelf,
        tags: set[str],
        date_started: datetime.date | None,
        date_stopped: datetime.date | None,
        isbn13: str | None,
        data: typing.Mapping[str, typing.Any],
    ):
        log = logger.bind(entry_id=entry_id, title=title, author=author)
        if entry := self.get_entry(entry_id):
            log.info("Updating existing Goodreads book")
        else:
            log.info("Creating new Goodreads book")
            entry = GoodreadsPrivateBook(id=entry_id)

        if title:
            entry.title = title
        if author:
            entry.author = author
        if release_date:
            entry.release_date = release_date
        if cover:
            entry.cover = cover
        if shelf:
            entry.shelf = shelf
        if tags:
            entry.tags = tags

        if entry.data is None:
            entry.data = {}

        entry.data.update(data)  # type: ignore
        flag_modified(entry, "data")

        if isbn13:
            entry.data["isbn13"] = isbn13  # type: ignore
            flag_modified(entry, "data")

        if not entry.work:
            work_id = self.reproducible_uuid(entry_id)
            entry.work = Book(user_id=self.user.id, id=work_id, shelf=shelf)

        if date_started or date_stopped:
            record_id = self.reproducible_uuid(entry_id)
            record = self.get_record(record_id) or Record(id=record_id)
            if date_started:
                record.date_started = date_started
            if date_stopped:
                record.date_stopped = date_stopped
            entry.work.records.append(record)

        return entry
