import typing

import flask.sansio.blueprints
import flask_login
import structlog

from vancelle.forms.work import WorksIndexForm
from vancelle.controllers.work import WorkController, WorkQuery
from vancelle.html.vancelle.pages.board import BoardPage
from vancelle.models import Work

logger = structlog.get_logger(logger_name=__name__)

controller = WorkController()

bp = flask.Blueprint("board", __name__, url_prefix="/board")


@bp.before_request
@flask_login.login_required
def before_request():
    pass


@bp.route("/", methods={"GET"})
def index():
    form = WorksIndexForm(formdata=flask.request.args, meta={"csrf": False})

    query = WorkQuery(
        user=flask_login.current_user,
        work_type=form.work_type.data,
        work_shelf=form.work_shelf.data,
        work_case=form.work_case.data,
        work_deleted=form.work_deleted.data,
        remote_type=form.remote_type.data,
        remote_data=form.remote_data.data,
        search=form.search.data,
    )

    shelves, total = query.shelves()
    return BoardPage(
        form=form,
        shelves=shelves,
        total=total,
        layout=form.layout.data,
    ).render()


@bp.route("/<work_type:work_type>/", methods={"GET"})
def work_type_index(work_type: typing.Type[Work]):
    raise NotImplementedError
