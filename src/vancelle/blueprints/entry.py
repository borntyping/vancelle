import uuid

import flask
import flask_login
import svcs
from werkzeug.exceptions import NotFound

from ..clients.images.client import ImageCache
from ..controllers.entry import EntryController
from ..controllers.work import WorkController
from ..extensions import htmx
from ..forms.entry import EntryIndexArgs
from ..html.vancelle.pages.entry import EntryDetailPage, EntryIndexPage
from ..lib.heavymetal import render
from ..models.entry import Entry

controller = EntryController()
work_controller = WorkController()

bp = flask.Blueprint("entry", __name__, url_prefix="/entries")


@bp.before_request
@flask_login.login_required
def before_request():
    pass


@bp.route("/")
@bp.route("/<string:entry_type>/")
def index(entry_type: str | None):
    entry_type = Entry.get_subclass_or_404(entry_type)
    entry_index_args = EntryIndexArgs(formdata=flask.request.args)
    items = entry_index_args.paginate()

    return render(
        EntryIndexPage(
            items=items,
            entry_type=entry_type,
            entry_index_args=entry_index_args,
        )
    )


@bp.route("/<string:entry_type>/<string:entry_id>")
def detail(entry_type: str, entry_id: str):
    entry = controller.get_or_404(entry_type, entry_id)

    return render(EntryDetailPage(entry))


@bp.route("/<string:entry_type>/<string:entry_id>/cover")
def cover(entry_type: str, entry_id: str):
    entry = controller.get_or_404(entry_type, entry_id)
    if not entry.cover:
        raise NotFound("Entry has no cover image.")
    return svcs.flask.get(ImageCache).as_response(entry.cover)


@bp.route("/<string:entry_type>/<string:entry_id>/background")
def background(entry_type: str, entry_id: str):
    entry = controller.get_or_404(entry_type, entry_id)
    if not entry.background:
        raise NotFound("Entry has no background image.")
    return svcs.flask.get(ImageCache).as_response(entry.background)


@bp.route("/<string:entry_type>/<string:entry_id>/-/create-work", methods={"post"})
def create_work(entry_type: str, entry_id: str):
    work = controller.create_work(entry_type=entry_type, entry_id=entry_id, user=flask_login.current_user)
    return htmx.redirect(work.url_for())


@bp.route("/<string:entry_type>/<string:entry_id>/-/refresh", methods={"post"})
def refresh(entry_type: str, entry_id: str):
    controller.refresh(entry_type=entry_type, entry_id=entry_id)

    return htmx.refresh()


@bp.route("/<string:entry_type>/<string:entry_id>/-/delete", methods={"post"})
def delete(entry_type: str, entry_id: str):
    controller.delete(entry_type=entry_type, entry_id=entry_id)
    return htmx.refresh()


@bp.route("/<string:entry_type>/<string:entry_id>/-/restore", methods={"post"})
def restore(entry_type: str, entry_id: str):
    controller.restore(entry_type=entry_type, entry_id=entry_id)
    return htmx.refresh()


@bp.route("/<string:entry_type>/<string:entry_id>/-/permanently-delete", methods={"post"})
def permanently_delete(entry_type: str, entry_id: str):
    controller.permanently_delete(entry_type=entry_type, entry_id=entry_id)
    return htmx.refresh()


@bp.route("/works/<uuid:work_id>/-/link-work", methods={"post"})
def link_work(work_id: uuid.UUID):
    entry_type = flask.request.args["entry_type"]
    entry_id = flask.request.args["entry_id"]

    work = controller.link_work(work_id=work_id, entry_type=entry_type, entry_id=entry_id)
    return htmx.redirect(work.url_for())
