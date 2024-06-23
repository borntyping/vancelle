import flask_login
import werkzeug.exceptions
import markupsafe
import wtforms.validators
from sqlalchemy import ColumnElement, Select, True_, desc, select
from sqlalchemy.orm import joinedload

from vancelle.extensions import db
from vancelle.forms.pagination import PaginationArgs
from vancelle.html.bootstrap.forms.controls import form_control
from vancelle.lib.pagination import Pagination
from vancelle.models import Remote, Work


class RemoteIndexArgs(PaginationArgs):
    class Meta:
        csrf = False

        def render_field(self, field: wtforms.Field, kwargs) -> markupsafe.Markup:
            return form_control(field, **kwargs)

    type = wtforms.SelectField(
        label="Remote type",
        choices=[("all", "All remotes")]
        + [(cls.polymorphic_identity(), cls.info.noun_full) for cls in Remote.iter_subclasses()],
        default="all",
        validators=[wtforms.validators.Optional()],
    )
    deleted = wtforms.SelectField(
        label="Deleted remotes",
        choices=[
            ("no", "Exclude deleted remotes"),
            ("any", "Include all remotes"),
            ("yes", "Only deleted remotes"),
        ],
        default="no",
        validators=[wtforms.validators.DataRequired()],
    )
    search = wtforms.SearchField(
        label="Search",
        validators=[wtforms.validators.Optional()],
    )

    def paginate(self) -> Pagination:
        return self.query(db.session, self._statement())

    def _statement(self) -> Select[tuple[Remote]]:
        return (
            select(Remote)
            .options(joinedload(Remote.work))
            .join(Work)
            .filter(Work.user_id == flask_login.current_user.id)
            .filter(self._filter_type(self.type.data))
            .filter(self._filter_deleted(self.deleted.data))
            .order_by(desc(Remote.time_updated), desc(Remote.time_created))
        )

    @staticmethod
    def _filter_type(value: str) -> ColumnElement[bool]:
        match value:
            case "all":
                return True_()
            case _:
                return Remote.type == value

    @staticmethod
    def _filter_deleted(value: str) -> ColumnElement[bool]:
        match value:
            case "no":
                return Remote.time_deleted.is_(None)
            case "any":
                return True_()
            case "yes":
                return Remote.time_deleted.is_not(None)

        raise werkzeug.exceptions.BadRequest("Invalid work deleted filter")
