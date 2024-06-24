import flask_login
import sqlalchemy
import wtforms.validators
from sqlalchemy import ColumnElement, Select, True_, desc, select
from sqlalchemy.orm import joinedload

from vancelle.extensions import db

from .bootstrap import BootstrapMeta
from .pagination import PaginationArgs
from vancelle.lib.pagination import Pagination
from vancelle.models import Entry, Work


class EntryIndexArgs(PaginationArgs):
    class Meta(BootstrapMeta):
        csrf = False

    entry_type = wtforms.SelectField(
        label="Entry type",
        choices=[("any", "Any entry type")] + [(cls.polymorphic_identity(), cls.info.noun_full) for cls in Entry.subclasses()],
        default="all",
        validators=[wtforms.validators.InputRequired()],
    )
    deleted = wtforms.SelectField(
        label="Deleted entries",
        choices=[
            ("no", "Exclude deleted entries"),
            ("any", "Include all entries"),
            ("yes", "Only deleted entries"),
        ],
        default="no",
        validators=[wtforms.validators.InputRequired()],
    )
    search = wtforms.SearchField(
        label="Search",
        validators=[wtforms.validators.Optional()],
    )

    def paginate(self) -> Pagination:
        return self.query(db.session, self._statement())

    def _statement(self) -> Select[tuple[Entry]]:
        return (
            select(Entry)
            .options(joinedload(Entry.work))
            .join(Work)
            .filter(Work.user_id == flask_login.current_user.id)
            .filter(self._filter_type(self.entry_type.data))
            .filter(self._filter_deleted(self.deleted.data))
            .filter(self._filter_search(self.search.data))
            .order_by(desc(Entry.time_updated), desc(Entry.time_created))
        )

    @staticmethod
    def _filter_type(value: str) -> ColumnElement[bool]:
        match value:
            case "any":
                return True_()
            case _:
                return Entry.type == value

    @staticmethod
    def _filter_deleted(value: str) -> ColumnElement[bool]:
        match value:
            case "no":
                return Entry.time_deleted.is_(None)
            case "any":
                return True_()
            case "yes":
                return Entry.time_deleted.is_not(None)

        raise ValueError(f"Invalid deleted filter ({value=})")

    @staticmethod
    def _filter_search(value: str) -> ColumnElement[bool]:
        match value:
            case None | "":
                return True_()
            case _:
                return sqlalchemy.or_(
                    Entry.title.ilike(f"%{value}%"),
                    Entry.author.ilike(f"%{value}%"),
                    Entry.series.ilike(f"%{value}%"),
                    Entry.description.ilike(f"%{value}%"),
                )
