import dataclasses
import datetime
import typing
import uuid

import flask
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
from vancelle.html.vancelle.pages.entry import EntrySearchPage
from vancelle.lib.heavymetal import render
from vancelle.lib.heavymetal.html import a, fragment
from vancelle.lib.pagination import Pagination
from vancelle.models import User
from vancelle.models.entry import Entry
from vancelle.models.work import Work
from vancelle.shelf import Shelf

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

    def _get_entry_from_db(self, *, entry_type: str, entry_id: str) -> Entry:
        return db.session.execute(self._statement(entry_type, entry_id, flask_login.current_user)).scalar_one()

    def _get_entry_from_db_or_none(self, *, entry_type: str, entry_id: str) -> Entry | None:
        return db.session.execute(self._statement(entry_type, entry_id, flask_login.current_user)).scalar_one_or_none()

    def _statement(self, entry_type: str, entry_id: str, user: User) -> sqlalchemy.Select[tuple[Entry]]:
        return (
            sqlalchemy.select(Entry)
            .join(Work)
            .options(sqlalchemy.joinedload(Entry.work))
            .filter(
                Entry.type == entry_type,
                Entry.id == entry_id,
                Work.user_id == user.id,
            )
        )

    def get_or_404(self, entry_type: str, entry_id: str, *, user: User = flask_login.current_user) -> Entry:
        if entry := db.session.execute(self._statement(entry_type, entry_id, user=user)).scalar_one_or_none():
            return entry

        raise NotFound(f"Entry {entry_type!r}:{entry_id!r} not found")

    # def get_entry(self, entry_type: str, entry_id: str) -> Entry:
    #     log = logger.bind(entry_type=entry_type, entry_id=entry_id)
    #
    #     if remote := self._get_remote_from_db_or_none(entry_type=entry_type, entry_id=entry_id):
    #         log.debug("Fetched remote from database")
    #         return remote
    #
    #     remote = self.managers[entry_type].fetch(entry_id)
    #     log.debug("Fetched remote from source")
    #     return remote

    def refresh(self, entry_type: str, entry_id: str) -> Entry:
        old_remote = self._get_entry_from_db(entry_type=entry_type, entry_id=entry_id)

        new_remote = self.managers[old_remote.type].fetch(old_remote.id)
        new_remote.work_id = old_remote.work_id

        assert new_remote.id == old_remote.id, f"{new_remote.id!r} != {old_remote.id!r}"

        db.session.merge(new_remote)
        db.session.commit()

        flask.flash(f"Refreshed {new_remote.info.noun_full} {new_remote.id}.", "Refreshed remote")
        return new_remote

    def delete(self, *, entry_type: str, entry_id: str) -> Entry:
        remote = self._get_entry_from_db(entry_type=entry_type, entry_id=entry_id)
        remote.time_deleted = sqlalchemy.func.now()
        db.session.add(remote)
        db.session.commit()
        return remote

    def restore(self, *, entry_type: str, entry_id: str) -> Entry:
        remote = self._get_entry_from_db(entry_type=entry_type, entry_id=entry_id)
        remote.time_deleted = None
        db.session.add(remote)
        db.session.commit()
        return remote

    def permanently_delete(self, *, entry_type: str, entry_id: str) -> None:
        remote = self._get_entry_from_db(entry_type=entry_type, entry_id=entry_id)
        db.session.delete(remote)
        db.session.commit()
        return None

    def create_work(self, *, entry_id: str, entry_type: str, user: User) -> Work:
        """
        Create a new remote and a new work.

        TODO: Move this to the SourceController.
        """

        if remote := self._get_entry_from_db_or_none(entry_type=entry_type, entry_id=entry_id):
            logger.info("Instructed to create a remote that already exists")
            flask.flash(
                render(fragment([a({"href": remote.url_for()}, [remote.title]), "is already attached to a work."])),
                "Remote already exists",
            )
            assert remote.work
            return remote.work

        manager = self.managers[entry_type]
        remote = manager.fetch(entry_id)
        assert not remote.work

        work = manager.work_type(
            id=uuid.uuid4(),
            user=user,
            remotes=[remote],
            shelf=self._assign_shelf(remote),
        )
        db.session.add(work)
        db.session.commit()
        return work

    def _assign_shelf(self, remote: Entry) -> Shelf:
        if remote.shelf is not None:
            return remote.shelf

        if not remote.release_date or remote.release_date > datetime.date.today():
            return Shelf.UNRELEASED

        return Shelf.UNSORTED

    def link_work(self, *, entry_id: str, entry_type: str, work_id: uuid.UUID) -> Work:
        """Create a new remote, linked to an existing work."""
        log = logger.bind(entry_id=entry_id, entry_type=entry_type, work_id=work_id)
        work = db.session.get(Work, work_id)

        # if remote := db.session.execute(
        #     select(Remote).filter(Remote.work_id == work_id, Remote.type == entry_type)
        # ).scalar_one_or_none():
        #     log.info("Remote already exists in database", remote=remote)
        #     raise Exception(f"Work already has a {entry_type} remote attached.")

        remote = self.managers[entry_type].fetch(entry_id)
        log.info("Fetched remote", remote=remote)
        work.entries.append(remote)
        db.session.add(work)
        db.session.commit()
        return work

    def render_search(
        self,
        *,
        entry_type: typing.Type[Entry],
        candidate_work_id: uuid.UUID | None,
        query: str | None,
    ) -> str:
        candidate_work: Work | None
        remote_items: Pagination

        if candidate_work_id:
            candidate_work = db.session.get(Work, candidate_work_id)
            candidate_work_details = candidate_work.resolve_details()
            query = query or candidate_work_details.title
        else:
            candidate_work = None

        if query:
            remote_items = self.managers[entry_type.polymorphic_identity()].search(query)
        else:
            remote_items = Pagination.empty()

        return render(EntrySearchPage(entry_type=entry_type, candidate_work=candidate_work, entry_items=remote_items))
