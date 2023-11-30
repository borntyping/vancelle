import uuid

import flask.sansio.blueprints
import flask_login
import flask_wtf
import structlog
import wtforms
from werkzeug.exceptions import BadRequest
from wtforms.validators import Optional

from vancelle.blueprints.bulma import BulmaSelect
from vancelle.controllers.work import WorkController
from vancelle.ext.wtforms import NullFilter
from vancelle.extensions import db, htmx
from vancelle.extensions.ext_html import Toggle
from vancelle.models import User
from vancelle.models.remote import Remote
from vancelle.models.work import Work
from vancelle.shelf import Shelf

logger = structlog.get_logger(logger_name=__name__)

controller = WorkController()

bp = flask.Blueprint("work", __name__, url_prefix="")


class WorkForm(flask_wtf.FlaskForm):
    type = wtforms.SelectField(
        "Type",
        choices=[(cls.identity(), cls.info.title) for cls in Work.iter_subclasses()],
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
        choices=[(s.value, s.title) for s in Shelf] + [("", "")],
        coerce=lambda x: Shelf(x) if x else None,  # type: ignore
        widget=BulmaSelect(),
        validators=[Optional()],
    )
    # tags = wtforms.StringField('tags')


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
        "home.html",
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
    layout = Toggle.from_request("layout", mapping={"board": "Board", "table": "Table"}, default="board")
    work_type = Toggle.from_request(
        "type",
        mapping={cls.identity(): cls.info.title for cls in Work.iter_subclasses()},
        args=dict(remote_type=None),
    )
    remote_type = Toggle.from_request(
        "remote_type",
        mapping={cls.identity(): cls.info.noun_full for cls in Remote.iter_subclasses()},
        args=dict(type=None),
    )
    has_remote = Toggle.from_request(
        "has_remote",
        mapping={
            "": "All",
            "yes": "Has remote data",
            "imported": "Has only imported data",
            "no": "No remote data",
        },
    )

    statement = controller.select(
        user=flask_login.current_user,
        work_type=work_type.value,
        remote_type=remote_type.value,
        has_remote=has_remote.value,
    )
    context = dict(
        layout=layout,
        work_type=work_type,
        remote_type=remote_type,
        has_remote=has_remote,
    )

    logger.debug("Loaded toggles", **context)

    match layout.value:
        case "board":
            shelves = controller.shelves(statement=statement)
            total = sum(len(v) for v in shelves.values())
            page = flask.render_template("work/index_board.html", **context, shelves=shelves, total=total)
        case "table":
            works = controller.table(statement=statement)
            page = flask.render_template("work/index_table.html", **context, works=works, total=works.total)
        case _:
            raise BadRequest(f"Unknown layout {layout!r}")

    response = flask.Response(page)
    response.set_cookie(layout.key, layout.value)
    response.set_cookie(work_type.key, work_type.value)
    response.set_cookie(remote_type.key, remote_type.value)
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
