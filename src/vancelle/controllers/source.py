import datetime
import typing
import uuid

import flask
import flask_login
import frozendict
import structlog

from .entry import EntryController
from .sources import Source
from vancelle.models import Entry, User, Work
from .work import WorkController
from ..extensions import db
from ..html.vancelle.components.flash import EntryAlreadyExistsFlash
from ..lib.heavymetal import render
from ..shelf import Shelf

logger = structlog.get_logger(logger_name=__name__)


class SourceController:
    work_controller = WorkController()
    entry_controller = EntryController()
    mapping: typing.Mapping[str, Source] = frozendict.frozendict({
        source.entry_type.polymorphic_identity(): source for source in Source.subclasses()
    })

    @property
    def sources(self) -> typing.Sequence[Source]:
        return list(self.mapping.values())

    def source(self, *, entry_type: str) -> Source:
        return self.mapping[entry_type]

    def fetch(self, *, entry_type: str, entry_id: str) -> Entry:
        entry = self.source(entry_type=entry_type).fetch(entry_id)
        entry.time_fetched = datetime.datetime.now()
        return entry

    def import_entry(
        self,
        *,
        entry_type: str,
        entry_id: str,
        work_id: uuid.UUID | None,
        user: User = flask_login.current_user,
    ) -> Work:
        """
        Attempt to import an entry.

        - If the entry already exists, redirect to that entry's work.
        - If a work_id is provided, attach the new entry to that work.
        - If a work_id is not provided, create a new work.
        """

        if entry := self.entry_controller.get(entry_type, entry_id, user=user):
            logger.info("Attempted to import an entry that already exists")
            flask.flash(render(EntryAlreadyExistsFlash(entry)), "Entry already exists")
            return entry.work

        entry = self.fetch(entry_type=entry_type, entry_id=entry_id)

        if work_id is not None:
            work = self.work_controller.get_or_404(work_id, user=user)
        else:
            work = self.source(entry_type=entry_type).work_type(id=uuid.uuid4(), user_id=user.id, shelf=self._shelve(entry))

        work.entries.append(entry)

        db.session.add(work)
        db.session.commit()
        return work

    def _shelve(self, entry: Entry) -> Shelf:
        if not entry.release_date:
            return Shelf.UNRELEASED

        if entry.release_date > datetime.date.today():
            return Shelf.UNRELEASED

        return Shelf.UNSORTED

    def refresh(self, *, entry_type: str, entry_id: str, user: User = flask_login.current_user) -> Entry:
        old_entry = self.entry_controller.get_or_404(entry_type, entry_id, user=user)

        new_entry = self.fetch(entry_type=entry_type, entry_id=entry_id)
        new_entry.work_id = old_entry.work_id

        assert new_entry.id == old_entry.id, f"{new_entry.id=} != {old_entry.id=}"

        db.session.merge(new_entry)
        db.session.commit()

        flask.flash(f"Refreshed {new_entry.resolve_title()}.", "Refreshed entry")
        return new_entry
