import uuid

import flask
import flask_login

from vancelle.controllers.source import SourceController
from vancelle.controllers.work import WorkController
from vancelle.forms.source import SourceSearchArgs
from vancelle.html.vancelle.pages.source import SourceDetailPage, ExternalSearchPage, ExternalIndexPage
from vancelle.lib.heavymetal import render

bp = flask.Blueprint("source", __name__, url_prefix="/sources")

controller = SourceController()
work_controller = WorkController()


@bp.before_request
@flask_login.login_required
def before_request():
    pass


@bp.route("/")
def index():
    return render(ExternalIndexPage(sources=controller.sources))


@bp.route("/<string:entry_type>")
def search(entry_type: str):
    args = SourceSearchArgs(formdata=flask.request.args)

    candidate_work_id = flask.request.args.get("candidate_work_id", type=uuid.UUID)
    candidate_work = work_controller.get(candidate_work_id)

    query = args.search.data or (candidate_work and candidate_work.resolve_title()) or ""
    items = controller[entry_type].search(query)

    return render(
        ExternalSearchPage(
            query=query,
            source=controller[entry_type],
            args=args,
            items=items,
            candidate_work=candidate_work,
        )
    )


@bp.route("/<string:entry_type>/<string:entry_id>", methods={"get"})
def detail(entry_type: str, entry_id: str):
    source = controller[entry_type]
    entry = source.fetch(entry_id)

    candidate_work_id = flask.request.args.get("work_id", type=uuid.UUID)
    candidate_work = work_controller.get(candidate_work_id)

    return SourceDetailPage(source=source, entry=entry, candidate_work=candidate_work)


@bp.route("/<string:entry_type>/<string:entry_id>/-/import", methods={"post"}, endpoint="import")
def import_from_source(entry_type: str, entry_id: str):
    source = controller[entry_type]
    entry = source.fetch(entry_id)

    candidate_work_id = flask.request.args.get("work_id", type=uuid.UUID)
    candidate_work = work_controller.get(candidate_work_id)

    raise NotImplementedError
