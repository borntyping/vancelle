import uuid

import flask
import flask_login

from vancelle.controllers.source import ExternalRemoteController
from vancelle.controllers.work import WorkController
from vancelle.forms.source import SourceSearchArgs
from vancelle.html.vancelle.pages.source import ExternalDetailPage, ExternalSearchPage, ExternalIndexPage
from vancelle.lib.heavymetal import render

bp = flask.Blueprint("source", __name__, url_prefix="/sources")

controller = ExternalRemoteController()
work_controller = WorkController()


@bp.before_request
@flask_login.login_required
def before_request():
    pass


@bp.route("/")
def index():
    return render(ExternalIndexPage(sources=controller.sources))


@bp.route("/<string:remote_type>")
def search(remote_type: str):
    source = controller[remote_type]
    args = SourceSearchArgs(formdata=flask.request.args)

    candidate_work_id = flask.request.args.get("candidate_work_id", type=uuid.UUID)
    candidate_work = work_controller.get(id=candidate_work_id)

    query = args.search.data or (candidate_work and candidate_work.resolve_title()) or ""
    items = source.search(query)

    return render(
        ExternalSearchPage(
            query=query,
            source=source,
            args=args,
            items=items,
            candidate_work=candidate_work,
        )
    )


@bp.route("/<string:remote_type>/<string:remote_id>")
def detail(remote_type: str, remote_id: str):
    remote_source = controller[remote_type]
    remote = remote_source.fetch(remote_id)

    candidate_work_id = flask.request.args.get("work_id", type=uuid.UUID)
    candidate_work = work_controller.get(id=candidate_work_id)

    return ExternalDetailPage(
        remote_source=remote_source,
        remote=remote,
        candidate_work=candidate_work,
    )
