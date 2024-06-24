import dataclasses
import typing

import flask_login
import sqlalchemy
import structlog
from werkzeug.exceptions import NotFound

from vancelle.controllers.sources import (
    GoodreadsPublicBookSource,
    ImportedWorkSource,
    OpenlibraryEditionSource,
    OpenlibraryWorkSource,
    RoyalroadFictionSource,
    Source,
    SteamApplicationSource,
    TmdbMovieSource,
    TmdbTvSeriesSource,
)
from vancelle.controllers.sources.goodreads import GoodreadsPrivateBookSource
from vancelle.extensions import db
from vancelle.models import User
from vancelle.models.entry import Entry
from vancelle.models.work import Work

logger = structlog.get_logger(logger_name=__name__)


DEFAULT_MANAGERS = (
    GoodreadsPrivateBookSource(),
    GoodreadsPublicBookSource(),
    OpenlibraryWorkSource(),
    OpenlibraryEditionSource(),
    ImportedWorkSource(),
    RoyalroadFictionSource(),
    SteamApplicationSource(),
    TmdbMovieSource(),
    TmdbTvSeriesSource(),
)


@dataclasses.dataclass(init=False)
class EntryController:
    managers: typing.Mapping[str, Source]

    def __init__(self, managers: typing.Iterable[Source] = DEFAULT_MANAGERS) -> None:
        self.managers = {m.entry_type.polymorphic_identity(): m for m in managers}

        for cls in Entry.subclasses():
            if cls.polymorphic_identity() not in self.managers:
                raise NotImplementedError(f"No manager registered for {cls.polymorphic_identity()} ({cls.info=})")

    def get(self, entry_type: str, entry_id: str, *, user: User = flask_login.current_user) -> Entry:
        statement = (
            sqlalchemy.select(Entry)
            .join(Work)
            .options(sqlalchemy.orm.joinedload(Entry.work))
            .filter(Entry.type == entry_type, Entry.id == entry_id, Work.user_id == user.id)
        )

        return db.session.execute(statement).scalar_one_or_none()

    def get_or_404(self, entry_type: str, entry_id: str, *, user: User = flask_login.current_user) -> Entry:
        if entry := self.get(entry_type, entry_id, user=user):
            return entry

        raise NotFound(f"Entry {entry_type!r}:{entry_id!r} not found")

    def delete(self, *, entry_type: str, entry_id: str) -> Entry:
        entry = self.get_or_404(entry_type=entry_type, entry_id=entry_id)
        entry.time_deleted = sqlalchemy.func.now()
        db.session.add(entry)
        db.session.commit()
        return entry

    def restore(self, *, entry_type: str, entry_id: str) -> Entry:
        entry = self.get_or_404(entry_type=entry_type, entry_id=entry_id)
        entry.time_deleted = None
        db.session.add(entry)
        db.session.commit()
        return entry

    def permanently_delete(self, *, entry_type: str, entry_id: str) -> None:
        entry = self.get_or_404(entry_type=entry_type, entry_id=entry_id)
        db.session.delete(entry)
        db.session.commit()
        return None
