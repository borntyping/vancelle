import uuid

import flask
import flask_login

from vancelle.controllers.source import SourceController
from vancelle.controllers.work import WorkController
from vancelle.extensions import htmx
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
    return render(ExternalIndexPage())


@bp.route("/<string:entry_type>")
def search(entry_type: str):
    args = SourceSearchArgs(formdata=flask.request.args)

    work_id = flask.request.args.get("work_id", type=uuid.UUID)
    work = work_controller.get(work_id)

    query = args.search.data or (work and work.resolve_title()) or ""
    source = controller.source(entry_type=entry_type)
    items = controller.search(entry_type=entry_type, query=query)

    return render(
        ExternalSearchPage(
            query=query,
            source=source,
            args=args,
            items=items,
            work=work,
        )
    )


@bp.route("/<string:entry_type>/<string:entry_id>", methods={"get"})
def detail(entry_type: str, entry_id: str):
    work_id = flask.request.args.get("work_id", type=uuid.UUID)

    source = controller.source(entry_type=entry_type)
    entry = controller.fetch(entry_type=entry_type, entry_id=entry_id)
    work = work_controller.get(work_id)

    return render(SourceDetailPage(source=source, entry=entry, work=work))


@bp.route("/<string:entry_type>/<string:entry_id>/-/import", methods={"post"}, endpoint="import")
def import_(entry_type: str, entry_id: str):
    work_id = flask.request.args.get("work_id", type=uuid.UUID)

    work = controller.import_entry(entry_type=entry_type, entry_id=entry_id, work_id=work_id)

    return htmx.redirect(work.url_for())


@bp.route("/<string:entry_type>/<string:entry_id>/-/refresh", methods={"post"})
def refresh(entry_type: str, entry_id: str):
    controller.refresh(entry_type=entry_type, entry_id=entry_id)

    return htmx.refresh()
