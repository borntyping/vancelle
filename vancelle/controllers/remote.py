import dataclasses
import typing
import uuid

import sqlalchemy
import structlog
from flask_sqlalchemy.pagination import Pagination
from sqlalchemy import select

from vancelle.controllers.sources.base import Manager
from vancelle.controllers.sources.goodreads import GoodreadsBookManager
from vancelle.controllers.sources.imported import ImportedWorkManager
from vancelle.controllers.sources.openlibrary import OpenlibraryEditionManager, OpenlibraryWorkManager
from vancelle.controllers.sources.royalroad import RoyalroadFictionManager
from vancelle.controllers.sources.steam import SteamApplicationManager
from vancelle.controllers.sources.tmdb import TmdbMovieManager, TmdbTvSeriesManager
from vancelle.ext.flask_sqlalchemy import EmptyPagination
from vancelle.extensions import db
from vancelle.models import User
from vancelle.models.remote import Remote
from vancelle.models.work import Work

logger = structlog.get_logger(logger_name=__name__)


DEFAULT_MANAGERS = (
    GoodreadsBookManager(),
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
        self.managers = {m.remote_type.identity(): m for m in managers}

        for cls in Remote.iter_subclasses():
            if cls.identity() not in self.managers:
                raise NotImplementedError(f"No manager registered for {cls.identity()} ({cls.info=})")

    def __getitem__(self, item: str) -> Manager:
        return self.managers[item]

    def render_template(self, name: str, remote_type: str, **context: typing.Any) -> str:
        return self.managers[remote_type].render_template(name, remote_type=remote_type, **context)

    def _get_work_by_id(self, work_id: uuid.UUID) -> Work:
        return db.get_or_404(Work, work_id, description="Work not found")

    def _get_remote_from_db(self, *, remote_type: str, remote_id: str) -> Remote:
        log = logger.bind(remote_type=remote_type, remote_id=remote_id)
        remote = db.one_or_404(
            select(Remote).filter(Remote.type == remote_type, Remote.id == remote_id),
            description="Remote not found",
        )
        log.debug("Fetched remote from database", id=remote.id)
        return remote

    def _get_remote(self, *, remote_type: str, remote_id: str) -> Remote:
        log = logger.bind(remote_type=remote_type, remote_id=remote_id)

        if remote := db.session.execute(
            select(Remote).filter(Remote.type == remote_type, Remote.id == remote_id)
        ).scalar_one_or_none():
            log.debug("Fetched remote from database")
            return remote

        remote = self[remote_type].fetch(remote_id)
        log.debug("Fetched remote from source")
        return remote

    def index(self, *, remote_type: str | None) -> Pagination:
        query = sqlalchemy.select(Remote)

        if remote_type is not None:
            query = query.filter(Remote.type == remote_type)

        return db.paginate(query)

    def refresh(self, remote_type: str, remote_id: str) -> Remote:
        old_remote = self._get_remote_from_db(remote_type=remote_type, remote_id=remote_id)

        new_remote = self[old_remote.type].fetch(old_remote.id)
        new_remote.work_id = old_remote.work_id

        assert new_remote.id == old_remote.id, f"{new_remote.id!r} != {old_remote.id!r}"

        db.session.merge(new_remote)
        db.session.commit()
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
        """Create a new remote and a new work."""
        remote = self[remote_type].fetch(remote_id)
        source = remote.info
        work = Work(
            id=uuid.uuid4(),
            user=user,
            type=source.work_type,
            remotes=[remote],
        )
        db.session.add(work)
        db.session.commit()
        return work

    def link_work(self, *, remote_id: str, remote_type: str, work_id: uuid.UUID) -> Work:
        """Create a new remote, linked to an existing work."""
        log = logger.bind(remote_id=remote_id, remote_type=remote_type, work_id=work_id)
        work = self._get_work_by_id(work_id=work_id)

        # if remote := db.session.execute(
        #     select(Remote).filter(Remote.work_id == work_id, Remote.type == remote_type)
        # ).scalar_one_or_none():
        #     log.info("Remote already exists in database", remote=remote)
        #     raise Exception(f"Work already has a {remote_type} remote attached.")

        remote = self[remote_type].fetch(remote_id)
        log.info("Fetched remote", remote=remote)
        work.remotes.append(remote)
        db.session.add(work)
        db.session.commit()
        return work

    def render_search(self, *, work_id: uuid.UUID | None, remote_type: str, query: str) -> str:
        work: Work | None
        query: str
        items: Pagination

        if work_id:
            work = self._get_work_by_id(work_id)
            query = query or work.resolve_details().title
        else:
            work = None

        if query:
            items = self[remote_type].search(query)
        else:
            items = EmptyPagination()

        return self.render_template("search.html", remote_type=remote_type, work=work, query=query, items=items)

    def render_detail(self, *, remote_type: str, remote_id: str, work_id: uuid.UUID | None) -> str:
        remote = self._get_remote(remote_type=remote_type, remote_id=remote_id)
        work = self._get_work_by_id(work_id) if work_id else None
        context = self.managers[remote_type].context_detail(remote)
        return self.render_template("detail.html", remote_type=remote_type, remote=remote, work=work, **context)
