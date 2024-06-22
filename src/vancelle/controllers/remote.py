import dataclasses
import datetime
import typing
import uuid

import flask
import sqlalchemy
import structlog

from vancelle.controllers.sources.base import Manager
from vancelle.controllers.sources.goodreads import GoodreadsPrivateBookManager, GoodreadsPublicBookManager
from vancelle.controllers.sources.imported import ImportedWorkManager
from vancelle.controllers.sources.openlibrary import OpenlibraryEditionManager, OpenlibraryWorkManager
from vancelle.controllers.sources.royalroad import RoyalroadFictionManager
from vancelle.controllers.sources.steam import SteamApplicationManager
from vancelle.controllers.sources.tmdb import TmdbMovieManager, TmdbTvSeriesManager
from vancelle.extensions import db
from vancelle.html.vancelle.pages.remote import remote_search_page
from vancelle.lib.heavymetal import render
from vancelle.lib.heavymetal.html import a, fragment
from vancelle.lib.pagination import Pagination
from vancelle.lib.pagination.flask import FlaskPaginationArgs
from vancelle.models import User
from vancelle.models.remote import Remote
from vancelle.models.work import Work
from vancelle.shelf import Shelf

logger = structlog.get_logger(logger_name=__name__)


DEFAULT_MANAGERS = (
    GoodreadsPrivateBookManager(),
    GoodreadsPublicBookManager(),
    OpenlibraryWorkManager(),
    OpenlibraryEditionManager(),
    ImportedWorkManager(),
    RoyalroadFictionManager(),
    SteamApplicationManager(),
    TmdbMovieManager(),
    TmdbTvSeriesManager(),
)


@dataclasses.dataclass(init=False)
class RemotesController:
    managers: typing.Mapping[str, Manager]

    def __init__(self, managers: typing.Iterable[Manager] = DEFAULT_MANAGERS) -> None:
        self.managers = {m.remote_type.remote_type(): m for m in managers}

        for cls in Remote.iter_subclasses():
            if cls.remote_type() not in self.managers:
                raise NotImplementedError(f"No manager registered for {cls.remote_type()} ({cls.info=})")

    def _get_remote_from_db(self, *, remote_type: str, remote_id: str) -> Remote:
        return db.session.execute(self._get_remote_query(remote_type=remote_type, remote_id=remote_id)).scalar_one()

    def _get_remote_from_db_or_none(self, *, remote_type: str, remote_id: str) -> Remote | None:
        return db.session.execute(self._get_remote_query(remote_type=remote_type, remote_id=remote_id)).scalar_one_or_none()

    def _get_remote_query(self, remote_type: str, remote_id: str) -> sqlalchemy.Select:
        return sqlalchemy.select(Remote).filter(Remote.type == remote_type, Remote.id == remote_id)

    def get_work(self, work_id: int | None) -> Work | None:
        return db.session.get(Work, work_id) if work_id else None

    def get_remote(self, remote_type: str, remote_id: str) -> Remote:
        log = logger.bind(remote_type=remote_type, remote_id=remote_id)

        if remote := self._get_remote_from_db_or_none(remote_type=remote_type, remote_id=remote_id):
            log.debug("Fetched remote from database")
            return remote

        remote = self.managers[remote_type].fetch(remote_id)
        log.debug("Fetched remote from source")
        return remote

    def index(self, *, remote_type: typing.Type[Remote] | None) -> Pagination:
        args = FlaskPaginationArgs()
        query = sqlalchemy.select(Remote).join(Work)

        if remote_type is not None:
            query = query.filter(Remote.type == remote_type.__mapper__.polymorphic_identity)

        return args.query(db.session, query)

    def refresh(self, remote_type: str, remote_id: str) -> Remote:
        old_remote = self._get_remote_from_db(remote_type=remote_type, remote_id=remote_id)

        new_remote = self.managers[old_remote.type].fetch(old_remote.id)
        new_remote.work_id = old_remote.work_id

        assert new_remote.id == old_remote.id, f"{new_remote.id!r} != {old_remote.id!r}"

        db.session.merge(new_remote)
        db.session.commit()

        flask.flash(f"Refreshed {new_remote.info.noun_full} {new_remote.id}.", "Refreshed remote")
        return new_remote

    def delete(self, *, remote_type: str, remote_id: str) -> Remote:
        remote = self._get_remote_from_db(remote_type=remote_type, remote_id=remote_id)
        remote.time_deleted = sqlalchemy.func.now()
        db.session.add(remote)
        db.session.commit()
        return remote

    def restore(self, *, remote_type: str, remote_id: str) -> Remote:
        remote = self._get_remote_from_db(remote_type=remote_type, remote_id=remote_id)
        remote.time_deleted = None
        db.session.add(remote)
        db.session.commit()
        return remote

    def permanently_delete(self, *, remote_type: str, remote_id: str) -> None:
        remote = self._get_remote_from_db(remote_type=remote_type, remote_id=remote_id)
        db.session.delete(remote)
        db.session.commit()
        return None

    def create_work(self, *, remote_id: str, remote_type: str, user: User) -> Work:
        """
        Create a new remote and a new work.
        """

        if remote := self._get_remote_from_db_or_none(remote_type=remote_type, remote_id=remote_id):
            logger.info("Instructed to create a remote that already exists")
            flask.flash(
                render(fragment([a({"href": remote.url_for()}, [remote.title]), "is already attached to a work."])),
                "Remote already exists",
            )
            assert remote.work
            return remote.work

        manager = self.managers[remote_type]
        remote = manager.fetch(remote_id)
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

    def _assign_shelf(self, remote: Remote) -> Shelf:
        if remote.shelf is not None:
            return remote.shelf

        if not remote.release_date or remote.release_date > datetime.date.today():
            return Shelf.UNRELEASED

        return Shelf.UNSORTED

    def link_work(self, *, remote_id: str, remote_type: str, work_id: uuid.UUID) -> Work:
        """Create a new remote, linked to an existing work."""
        log = logger.bind(remote_id=remote_id, remote_type=remote_type, work_id=work_id)
        work = db.session.get(Work, work_id)

        # if remote := db.session.execute(
        #     select(Remote).filter(Remote.work_id == work_id, Remote.type == remote_type)
        # ).scalar_one_or_none():
        #     log.info("Remote already exists in database", remote=remote)
        #     raise Exception(f"Work already has a {remote_type} remote attached.")

        remote = self.managers[remote_type].fetch(remote_id)
        log.info("Fetched remote", remote=remote)
        work.remotes.append(remote)
        db.session.add(work)
        db.session.commit()
        return work

    def render_search(
        self,
        *,
        remote_type: typing.Type[Remote],
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
            remote_items = self.managers[remote_type.remote_type()].search(query)
        else:
            remote_items = Pagination.empty()

        return render(remote_search_page(remote_type=remote_type, candidate_work=candidate_work, remote_items=remote_items))
        # return flask.render_template(
        #     [f"remote/{remote_type}/search.html", "remote/search.html"],
        #     remote_type=remote_type,
        #     remote_info=self.managers[remote_type].remote_type.info,
        #     work=candidate_work,
        #     query=query,
        #     items=remote_items,
        # )
