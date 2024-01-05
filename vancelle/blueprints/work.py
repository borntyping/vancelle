import itertools
import uuid

import flask.sansio.blueprints
import flask_login
import flask_wtf
import structlog
import wtforms
from werkzeug.exceptions import BadRequest
from wtforms.validators import DataRequired, Optional
from wtforms.widgets import HiddenInput

from vancelle.blueprints.bulma import BulmaSelect
from vancelle.controllers.work import WorkController, WorkQuery
from vancelle.ext.wtforms import NullFilter
from vancelle.extensions import db, htmx
from vancelle.models import User
from vancelle.models.remote import Remote
from vancelle.models.work import Work
from vancelle.shelf import Shelf, ShelfGroup

logger = structlog.get_logger(logger_name=__name__)

controller = WorkController()

bp = flask.Blueprint("work", __name__, url_prefix="")


class WorkForm(flask_wtf.FlaskForm):
    type = wtforms.SelectField(
        "Type",
        choices=[(cls.work_type(), cls.info.noun_title) for cls in Work.iter_subclasses()],
        widget=BulmaSelect(),
    )
    title = wtforms.StringField("Title", validators=[Optional()], filters=[NullFilter()])
    author = wtforms.StringField("Author", validators=[Optional()], filters=[NullFilter()])
    release_date = wtforms.DateField("Release Date", validators=[Optional()])
    description = wtforms.TextAreaField("Description", validators=[Optional()], filters=[NullFilter()])
    cover = wtforms.URLField("Cover image", validators=[Optional()], filters=[NullFilter()])
    background = wtforms.URLField("Background image", validators=[Optional()], filters=[NullFilter()])
    shelf = wtforms.SelectField(
        "Shelf",
        choices={
            shelf_group.title: [(s.value, s.title) for s in group]
            for shelf_group, group in itertools.groupby(Shelf, key=lambda shelf: shelf.group)
        },
        coerce=Shelf,
        default=Shelf.UNSORTED,
        widget=BulmaSelect(),
        validators=[Optional()],
    )
    # tags = wtforms.StringField('tags')


class WorkIndexForm(flask_wtf.FlaskForm):
    layout = wtforms.SelectField(
        label="Layout",
        choices=[
            ("board", "Board"),
            ("list", "List"),
            ("table", "Table"),
        ],
        default="board",
        widget=BulmaSelect(),
        validators=[DataRequired()],
    )
    work_type = wtforms.SelectField(
        label="Work type",
        choices=[("", "Any type")] + [(cls.work_type(), cls.info.noun_title) for cls in Work.iter_subclasses()],
        default="",
        widget=BulmaSelect(),
        validators=[Optional()],
    )
    work_shelf = wtforms.SelectField(
        label="Exact shelf",
        choices=[("", "Any shelf")] + [(s.value, s.title) for s in Shelf],
        default="",
        widget=BulmaSelect(),
        validators=[Optional()],
    )
    work_shelf_group = wtforms.SelectField(
        label="Shelf group",
        choices=[("", "Any shelf group")] + [(g.value, g.title) for g in ShelfGroup],
        default="",
        widget=BulmaSelect(),
        validators=[Optional()],
    )
    work_deleted = wtforms.SelectField(
        label="Deleted works",
        choices=[
            ("no", "Don't include deleted works"),
            ("all", "Include deleted works"),
            ("yes", "Only deleted works"),
        ],
        default="no",
        widget=BulmaSelect(),
        validators=[DataRequired()],
    )

    remote_type = wtforms.SelectField(
        label="Remote type",
        choices=[("", "Any remote type")] + [(cls.remote_type(), cls.info.noun_full) for cls in Remote.iter_subclasses()],
        default="",
        widget=BulmaSelect(),
        validators=[Optional()],
    )
    remote_data = wtforms.SelectField(
        label="Has remote",
        choices=[
            ("", "Any remote data"),
            ("yes", "Has remote data"),
            ("imported", "Only imported data"),
            ("no", "No remote data"),
        ],
        default="",
        widget=BulmaSelect(),
        validators=[Optional()],
    )
    search = wtforms.SearchField(label="Query", validators=[Optional()])


@bp.record_once
def setup(state: flask.sansio.blueprints.BlueprintSetupState):
    state.app.jinja_env.globals["Remote"] = Remote
    state.app.jinja_env.globals["Shelf"] = Shelf
    state.app.jinja_env.globals["Work"] = Work


@bp.before_request
@flask_login.login_required
def before_request():
    pass


@bp.route("/")
def home():
    return flask.render_template(
        "work/home.html",
        categories=[cls.info.plural for cls in Work.iter_subclasses()],
        works_count=controller.count(Work),
        remotes_count=controller.count(Remote),
        users_count=controller.count(User),
        works_count_by_type=controller.count_works_by_type(),
        remote_count_by_type=controller.count_remotes_by_type(),
    )


@bp.route("/works/-/create", methods={"get", "post"})
def create():
    form = WorkForm()

    if form.validate_on_submit():
        work = Work(id=uuid.uuid4(), user=flask_login.current_user)
        form.populate_obj(work)
        db.session.add(work)
        db.session.commit()
        return flask.redirect(work.url_for())

    return flask.render_template("work/create.html", form=form)


@bp.route("/works/")
def index():
    data = flask.json.loads(flask.request.cookies.get("index", "{}"))
    form = WorkIndexForm(formdata=flask.request.args, data=data, meta={"csrf": False})
    query = WorkQuery(
        user=flask_login.current_user,
        work_type=form.work_type.data,
        work_shelf=form.work_shelf.data,
        work_shelf_group=form.work_shelf_group.data,
        work_deleted=form.work_deleted.data,
        remote_type=form.remote_type.data,
        remote_data=form.remote_data.data,
        search=form.search.data,
    )

    match form.layout.data:
        case "board":
            shelves, total = query.shelves()
            page = flask.render_template(
                "work/index_board.html",
                form=form,
                layout=form.layout.data,
                shelves=shelves,
                total=total,
            )
        case "list":
            works = query.paginate()
            page = flask.render_template(
                "work/index_list.html",
                form=form,
                layout=form.layout.data,
                works=works,
                total=works.total,
            )
        case "table":
            works = query.paginate()
            page = flask.render_template(
                "work/index_table.html",
                form=form,
                layout=form.layout.data,
                works=works,
                total=works.total,
            )
        case _:
            raise BadRequest(f"Unknown layout {form.layout.data!r}")

    response = flask.Response(page)
    response.set_cookie("index", flask.json.dumps(form.data), samesite="Lax")
    return response


@bp.route("/works/<uuid:work_id>")
def detail(work_id: uuid.UUID):
    work = controller.get_or_404(id=work_id)
    form = WorkForm(obj=work)
    return flask.render_template("work/detail.html", work=work, form=form)


@bp.route("/works/<uuid:work_id>/-/update", methods={"get", "post"})
def update(work_id: uuid.UUID):
    work = controller.get_or_404(id=work_id)
    form = WorkForm(obj=work)

    if form.validate_on_submit():
        form.populate_obj(work)
        db.session.commit()
        return htmx.redirect(work.url_for())

    return flask.render_template("work/update.html", work=work, form=form)


@bp.route("/works/<uuid:work_id>/-/delete", methods={"post"})
def delete(work_id: uuid.UUID):
    controller.delete(controller.get_or_404(id=work_id))
    return htmx.refresh()


@bp.route("/works/<uuid:work_id>/-/restore", methods={"post"})
def restore(work_id: uuid.UUID):
    controller.restore(controller.get_or_404(id=work_id))
    return htmx.refresh()


@bp.route("/works/<uuid:work_id>/-/permanently-delete", methods={"post"})
def permanently_delete(work_id: uuid.UUID):
    controller.permanently_delete(controller.get_or_404(id=work_id))
    return htmx.redirect(flask.url_for(".index"))
