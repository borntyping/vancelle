import datetime
import itertools
import typing

import flask_login
import flask_wtf
import structlog
import wtforms.csrf.core
import wtforms.validators
from sqlalchemy import ColumnElement, Select, True_, desc, distinct, or_, select
from sqlalchemy.orm import aliased
from sqlalchemy.sql.functions import func

from vancelle.exceptions import ApplicationError
from vancelle.ext.wtforms import NoneFilter
from vancelle.extensions import db
from vancelle.forms.bootstrap import BootstrapMeta
from vancelle.forms.pagination import PaginationArgs
from vancelle.lib.pagination import Pagination
from vancelle.models import Record
from vancelle.models.entry import Entry, ImportedWork
from vancelle.models.work import Book, Work
from vancelle.shelf import Case, Shelf

SHELF_FORM_CHOICES = {
    group: [(shelf.value, shelf.title) for shelf in items]
    for group, items in itertools.groupby(Shelf, key=lambda shelf: shelf.group)
}

TYPE_FORM_CHOICES = [(cls.polymorphic_identity(), cls.info.noun_title) for cls in Work.subclasses()]

logger = structlog.get_logger(logger_name=__name__)


class WorkShelfForm(flask_wtf.FlaskForm):
    csrf_token: wtforms.csrf.core.CSRFTokenField

    shelf = wtforms.SelectField(
        "Shelf",
        choices=SHELF_FORM_CHOICES,
        coerce=Shelf,
        default=Shelf.UNSORTED,
        validators=[wtforms.validators.DataRequired()],
    )


class WorkForm(flask_wtf.FlaskForm):
    csrf_token: wtforms.csrf.core.CSRFTokenField

    type = wtforms.SelectField("Type", choices=TYPE_FORM_CHOICES, default=Book.polymorphic_identity())
    shelf = wtforms.SelectField("Shelf", coerce=Shelf, choices=SHELF_FORM_CHOICES, default=Shelf.UNSORTED)

    # Details
    title = wtforms.StringField("Title", validators=[wtforms.validators.Optional()], filters=[NoneFilter()])
    author = wtforms.StringField("Author", validators=[wtforms.validators.Optional()], filters=[NoneFilter()])
    series = wtforms.StringField("Series", validators=[wtforms.validators.Optional()], filters=[NoneFilter()])
    release_date = wtforms.DateField("Release Date", validators=[wtforms.validators.Optional()])
    description = wtforms.TextAreaField("Description", validators=[wtforms.validators.Optional()], filters=[NoneFilter()])
    cover = wtforms.URLField("Cover image", validators=[wtforms.validators.Optional()], filters=[NoneFilter()])
    background = wtforms.URLField("Background image", validators=[wtforms.validators.Optional()], filters=[NoneFilter()])
    # tags = wtforms.StringField('tags')

    # Properties
    external_url = wtforms.URLField("External URL", validators=[wtforms.validators.Optional()], filters=[NoneFilter()])
    isbn = wtforms.StringField("ISBN", validators=[wtforms.validators.Optional()], filters=[NoneFilter()])

    notes = wtforms.TextAreaField("Notes", validators=[wtforms.validators.Optional()], filters=[NoneFilter()])


class WorkIndexArgs(PaginationArgs):
    class Meta(BootstrapMeta):
        csrf = False

    work_type = wtforms.SelectField(
        label="Work type",
        choices=[("any", "Any work type")]
        + [(cls.polymorphic_identity(), cls.info.noun_plural_title) for cls in Work.subclasses()],
        default="any",
        validators=[wtforms.validators.InputRequired()],
    )
    shelf = wtforms.SelectField(
        label="Shelf",
        coerce=lambda x: None if x == "any" else Shelf(x),
        choices=[("any", "Any shelf")] + [(s.value, s.title) for s in Shelf],
        default="any",
        validators=[wtforms.validators.InputRequired()],
    )
    case = wtforms.SelectField(
        label="Case",
        coerce=lambda x: None if x == "any" else Case(x),
        choices=[("any", "Any case")] + [(g.value, g.title) for g in Case],
        default="any",
        validators=[wtforms.validators.InputRequired()],
    )
    deleted = wtforms.SelectField(
        label="Deleted",
        choices=[
            ("no", "Exclude deleted works"),
            ("any", "Include all works"),
            ("yes", "Only deleted works"),
        ],
        default="no",
        validators=[wtforms.validators.InputRequired()],
    )
    has_entry_type = wtforms.SelectField(
        label="Entry type",
        choices=[("any", "Any entry types")] + [(cls.polymorphic_identity(), cls.info.noun_full) for cls in Entry.subclasses()],
        default="any",
        validators=[wtforms.validators.InputRequired()],
    )
    has_entries = wtforms.SelectField(
        label="Has entries",
        choices=[
            ("any", "Works with and without entries"),
            ("yes", "Works with entries"),
            ("external", "Works with external entries"),
            ("imported", "Works with imported entries"),
            ("no", "Works without entries"),
        ],
        default="any",
        validators=[wtforms.validators.InputRequired()],
    )
    search = wtforms.SearchField(
        label="Search",
        validators=[wtforms.validators.Optional()],
    )

    @property
    def log(self) -> structlog.BoundLogger:
        return logger.bind(
            type=repr(self.work_type.data),
            shelf=repr(self.shelf.data),
            case=repr(self.case.data),
            deleted=repr(self.deleted.data),
            has_entry_type=repr(self.has_entry_type.data),
            has_entries=repr(self.has_entries.data),
            search=repr(self.search.data),
        )

    def paginate(self) -> Pagination:
        alias = aliased(Work, self._statement().subquery(name="w"))
        query = select(alias)

        count = query.with_only_columns(func.count(distinct(alias.id)))
        return self.query(db.session, query, count)

    def _statement(self) -> Select[tuple[Work]]:
        return (
            select(Work)
            .distinct()
            .filter(Work.user_id == flask_login.current_user.id)
            .filter(self._filter_work_type(self.work_type.data))
            .filter(self._filter_shelf(self.shelf.data))
            .filter(self._filter_case(self.case.data))
            .filter(self._filter_deleted(self.deleted.data))
            .filter(self._filter_has_entries(self.has_entries.data))
            .filter(self._filter_entry_type(self.has_entry_type.data))
            .filter(self._filter_search(self.search.data))
            .join(Record, isouter=True)
            .join(Entry, isouter=True)
            .order_by(desc(Work.time_updated), desc(Work.time_created))
        )

    @staticmethod
    def _filter_work_type(value: str) -> ColumnElement[bool]:
        return True_() if value == "any" else Work.type == value

    @staticmethod
    def _filter_shelf(shelf: Shelf | None) -> ColumnElement[bool]:
        return Work.shelf == shelf if shelf else True_()

    @staticmethod
    def _filter_case(case: Case) -> ColumnElement[bool]:
        return Work.shelf.in_(case.shelves) if case else True_()

    @staticmethod
    def _filter_entry_type(value: str) -> ColumnElement[bool]:
        return True_() if value == "any" else Entry.type == value

    @staticmethod
    def _filter_deleted(value: str) -> ColumnElement[bool]:
        match value:
            case "no":
                return Work.time_deleted.is_(None)
            case "any":
                return True_()
            case "yes":
                return Work.time_deleted.is_not(None)

        raise ValueError(f"Invalid deleted filter: {value!r}")

    @staticmethod
    def _filter_has_entries(value: str) -> ColumnElement[bool]:
        imported = ImportedWork.__mapper__.polymorphic_identity
        match value:
            case "any":
                return True_()
            case "yes":
                return Work.entries.any()
            case "external":
                return Work.entries.any(Entry.type != imported)
            case "imported":
                return Work.entries.any(Entry.type == imported)
            case "no":
                return ~Work.entries.any()
            case _:
                return Work.entries.any(Entry.type == value)

    @staticmethod
    def _filter_search(value: str | None) -> ColumnElement[bool]:
        match value:
            case None | "":
                return True_()
            case query:
                return or_(
                    Work.title.ilike(f"%{query}%"),
                    Work.author.ilike(f"%{query}%"),
                    Work.series.ilike(f"%{query}%"),
                    Work.description.ilike(f"%{query}%"),
                    Entry.title.ilike(f"%{query}%"),
                    Entry.author.ilike(f"%{query}%"),
                    Entry.series.ilike(f"%{query}%"),
                    Entry.description.ilike(f"%{query}%"),
                )

    def shelves(self) -> typing.Mapping[Shelf, list[Work]]:
        works = db.session.execute(self._statement()).unique().scalars()
        return self._group_shelves(works=works, shelf=self.shelf.data, case=self.case.data)

    @classmethod
    def _group_shelves(
        cls,
        works: typing.Iterable[Work],
        shelf: Shelf,
        case: Case,
    ) -> typing.Mapping[Shelf, list[Work]]:
        """
        All shelves in the selection (in 'work_case.shelves' or equal to 'work_shelf') will appear in the result even if empty.
        Other shelves will only be present in the result if the query somehow returned them.
        """
        groups: dict[Shelf, list[Work]] = {s: [] for s in cls._iter_shelves(shelf, case)}
        for work in works:
            groups[work.shelf].append(work)

        return {k: sorted(v, key=cls._work_sort_key, reverse=True) for k, v in groups.items()}

    @staticmethod
    def _iter_shelves(shelf: Shelf, case: Case) -> typing.Tuple[Shelf, ...]:
        if shelf and case:
            if shelf not in case.shelves:
                raise ApplicationError(f"The '{shelf.title}' shelf is not in the '{case.title}' group.")

        if shelf:
            return (shelf,)

        if case is not None:
            return case.shelves

        return tuple(Shelf)

    @classmethod
    def _work_sort_key(cls, work: Work) -> datetime.date | None:
        if key := cls._work_sort_coalesce(r.date_started or r.date_stopped or None for r in work.records):
            return key

        if key := cls._work_sort_coalesce(e.release_date for e in work.entries):
            return key

        if key := work.release_date:
            return key

        return work.time_created.date()

    @staticmethod
    def _work_sort_coalesce(iterable: typing.Iterable[datetime.date]) -> datetime.date | None:
        for item in sorted((item for item in iterable if item is not None), reverse=True):
            return item
        return None


class WorkBoardArgs(WorkIndexArgs):
    layout = wtforms.SelectField(
        label="Layout",
        choices={"vertical": "Vertical", "horizontal": "Horizontal"},
        default="vertical",
        validators=[wtforms.validators.DataRequired()],
    )
