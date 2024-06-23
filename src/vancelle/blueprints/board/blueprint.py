import typing

import flask.sansio.blueprints
import flask_login
import structlog

from vancelle.forms.work import WorkBoardArgs
from vancelle.controllers.work import WorkController
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
    form = WorkBoardArgs(formdata=flask.request.args)
    shelves, total = form.shelves()
    return BoardPage(
        form=form,
        shelves=shelves,
        total=total,
        layout=form.layout.data,
    ).render()


@bp.route("/<work_type:work_type>/", methods={"GET"})
def work_type_index(work_type: typing.Type[Work]):
    raise NotImplementedError
