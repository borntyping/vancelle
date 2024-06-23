import itertools
import typing

import flask_login
import flask_wtf
import markupsafe
import structlog
import werkzeug.exceptions
import wtforms.csrf.core
import wtforms.validators
from sqlalchemy import ColumnElement, Select, True_, desc, distinct, or_, select
from sqlalchemy.orm import aliased
from sqlalchemy.sql.functions import func

from vancelle.exceptions import ApplicationError
from vancelle.ext.wtforms import NoneFilter
from vancelle.extensions import db
from vancelle.forms.pagination import PaginationArgs
from vancelle.html.bootstrap.forms.controls import form_control
from vancelle.lib.pagination import Pagination
from vancelle.models import Record
from vancelle.models.remote import ImportedWork, Remote
from vancelle.models.work import Book, Work
from vancelle.shelf import Case, Shelf

SHELF_FORM_CHOICES = {
    group: [(shelf.value, shelf.title) for shelf in items]
    for group, items in itertools.groupby(Shelf, key=lambda shelf: shelf.group)
}

TYPE_FORM_CHOICES = [(cls.work_type(), cls.info.noun_title) for cls in Work.iter_subclasses()]

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


class WorkIndexArgs(PaginationArgs):
    class Meta:
        csrf = False

        def render_field(self, field: wtforms.Field, kwargs) -> markupsafe.Markup:
            return form_control(field, **kwargs)

    type = wtforms.SelectField(
        label="Work type",
        choices=[("", "All works")] + [(cls.work_type(), cls.info.noun_plural_title) for cls in Work.iter_subclasses()],
        default="",
        validators=[wtforms.validators.Optional()],
    )
    shelf = wtforms.SelectField(
        label="Exact shelf",
        coerce=lambda x: Shelf(x) if x else None,
        choices=[("", "All shelves")] + [(s.value, s.title) for s in Shelf],
        default="",
        validators=[wtforms.validators.Optional()],
    )
    case = wtforms.SelectField(
        label="Shelves",
        coerce=lambda x: Case(x) if x else None,
        choices=[("", "All shelves")] + [(g.value, g.title) for g in Case],
        default="",
        validators=[wtforms.validators.Optional()],
    )
    deleted = wtforms.SelectField(
        label="Deleted works",
        choices=[
            ("no", "Exclude deleted works"),
            ("any", "Include all works"),
            ("yes", "Only deleted works"),
        ],
        default="no",
        validators=[wtforms.validators.DataRequired()],
    )
    has_remote_type = wtforms.SelectField(
        label="Remote type",
        choices=[("", "All remote types")] + [(cls.remote_type(), cls.info.noun_full) for cls in Remote.iter_subclasses()],
        default="",
        validators=[wtforms.validators.Optional()],
    )
    has_remotes = wtforms.SelectField(
        label="Has remote metadata",
        choices=[
            ("", "All works"),
            ("yes", "Works with remote metadata"),
            ("imported", "Works with imported metadata"),
            ("no", "Works without remote metadata"),
        ],
        default="",
        validators=[wtforms.validators.Optional()],
    )
    search = wtforms.SearchField(
        label="Search",
        validators=[wtforms.validators.Optional()],
    )

    @property
    def log(self) -> structlog.BoundLogger:
        return logger.bind(
            type=repr(self.type.data),
            shelf=repr(self.shelf.data),
            case=repr(self.case.data),
            deleted=repr(self.deleted.data),
            has_remote_type=repr(self.has_remote_type.data),
            has_remotes=repr(self.has_remotes.data),
            search=repr(self.search.data),
        )

    def paginate(self) -> Pagination:
        alias = aliased(Work, self._statement().subquery(name="w"))
        query = select(alias)

        count = query.with_only_columns(func.count(distinct(alias.id)))
        return self.query(db.session, query, count)

    def shelves(self) -> typing.Tuple[typing.Mapping[Shelf, list[Work]], int]:
        """
        All shelves in the selection (in 'work_case.shelves' or equal to 'work_shelf') will appear in the result even if empty.
        Other shelves will only be present in the result if the query somehow returned them.
        """
        works = db.session.execute(self._statement()).unique().scalars()

        groups: dict[Shelf, list[Work]] = {
            shelf: []
            for shelf in self._iter_shelves(
                shelf=self.shelf.data,
                case=self.case.data,
            )
        }
        for work in works:
            groups[work.shelf].append(work)
        return groups, 0

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

    def _statement(self) -> Select[tuple[Work]]:
        self.log.info("Constructing query")
        statement = (
            select(Work)
            .distinct()
            .filter(Work.user_id == flask_login.current_user.id)
            .join(Record, isouter=True)
            .join(Remote, isouter=True)
            .order_by(desc(Work.time_updated), desc(Work.time_created))
        )

        statement = statement.filter(self._filter_work_deleted(self.deleted.data))

        if self.type.data:
            statement = statement.filter(Work.type == self.type.data)
        if self.shelf.data:
            statement = statement.filter(Work.shelf == self.shelf.data)
        if self.case.data:
            statement = statement.filter(Work.shelf.in_(self.case.data))
        if self.has_remote_type.data:
            statement = statement.filter(Remote.type == self.has_remote_type.data)
        if self.has_remotes.data:
            statement = statement.filter(self._filter_has_remotes(self.has_remotes.data))
        if self.search.data:
            statement = statement.filter(self._filter_search(self.search.data))

        self.log.info("Constructed query", statement=str(statement))
        return statement

    @staticmethod
    def _filter_search(query: str) -> ColumnElement[bool]:
        other = f"%{query}%"
        return or_(
            Work.title.ilike(other),
            Work.author.ilike(other),
            Work.series.ilike(other),
            Work.description.ilike(other),
            Remote.title.ilike(other),
            Remote.author.ilike(other),
            Remote.series.ilike(other),
            Remote.description.ilike(other),
        )

    @staticmethod
    def _filter_work_deleted(value: str) -> ColumnElement[bool]:
        match value:
            case "yes":
                return Work.time_deleted.is_not(None)
            case "no":
                return Work.time_deleted.is_(None)
            case "any":
                return True_()

        raise werkzeug.exceptions.BadRequest("Invalid work deleted filter")

    @staticmethod
    def _filter_has_remotes(value: str) -> ColumnElement[bool]:
        imported = ImportedWork.__mapper__.polymorphic_identity
        match value:
            case "yes":
                return Work.remotes.any()
            case "remote":
                return ~Work.remotes.any(Remote.type == imported)
            case "imported":
                return ~Work.remotes.any(Remote.type != imported)
            case "no":
                return ~Work.remotes.any()

        raise werkzeug.exceptions.BadRequest("Invalid remote data filter")


class WorkBoardArgs(WorkIndexArgs):
    layout = wtforms.SelectField(
        label="Layout",
        choices={"vertical": "Vertical", "horizontal": "Horizontal"},
        default="vertical",
        validators=[wtforms.validators.DataRequired()],
    )
