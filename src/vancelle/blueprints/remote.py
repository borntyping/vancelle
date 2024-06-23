import typing
import uuid

import flask
import flask_login
import svcs
from werkzeug.exceptions import NotFound

from ..clients.images.client import ImageCache
from ..controllers.remote import RemotesController
from ..extensions import db, htmx
from ..forms.remote import RemoteIndexArgs
from ..html.vancelle.pages.remote import RemoteDetailPage, RemoteIndexPage, RemoteSearchPage
from ..lib.heavymetal import render
from ..lib.pagination import Pagination
from ..models import Work
from ..models.remote import Remote

controller = RemotesController()

bp = flask.Blueprint("remote", __name__)


@bp.before_request
@flask_login.login_required
def before_request():
    pass


@bp.route("/remotes/")
@bp.route("/remotes/<remote_type:remote_type>/")
def index(remote_type: typing.Type[Remote] | None = None):
    remote_index_args = RemoteIndexArgs(formdata=flask.request.args)
    remotes = remote_index_args.paginate()

    return render(RemoteIndexPage(items=remotes, remote_type=remote_type, remote_index_args=remote_index_args))


@bp.route("/remotes/<string:remote_type>/<string:remote_id>")
def detail(remote_type: str, remote_id: str):
    remote = controller.get_remote(remote_type=remote_type, remote_id=remote_id)

    candidate_work_id = flask.request.args.get("work_id", type=uuid.UUID)
    candidate_work = controller.get_work(work_id=candidate_work_id)

    return render(RemoteDetailPage(remote, candidate_work=candidate_work))


@bp.route("/remotes/<string:remote_type>/<string:remote_id>/cover")
def cover(remote_type: str, remote_id: str):
    images = svcs.flask.get(ImageCache)
    remote = controller.get_remote(remote_type=remote_type, remote_id=remote_id)
    if not remote.cover:
        raise NotFound("Remote has no cover image.")
    return images.as_response(remote.cover)


@bp.route("/remotes/<string:remote_type>/<string:remote_id>/background")
def background(remote_type: str, remote_id: str):
    images = svcs.flask.get(ImageCache)
    remote = controller.get_remote(remote_type=remote_type, remote_id=remote_id)
    if not remote.background:
        raise NotFound("Remote has no background image.")
    return images.as_response(remote.background)


@bp.route("/remotes/<string:remote_type>/<string:remote_id>/-/create-work", methods={"post"})
def create_work(remote_type: str, remote_id: str):
    work = controller.create_work(remote_type=remote_type, remote_id=remote_id, user=flask_login.current_user)
    return htmx.redirect(work.url_for())


@bp.route("/remotes/<string:remote_type>/<string:remote_id>/-/refresh", methods={"post"})
def refresh(remote_type: str, remote_id: str):
    controller.refresh(remote_type=remote_type, remote_id=remote_id)

    return htmx.refresh()


@bp.route("/remotes/<string:remote_type>/<string:remote_id>/-/delete", methods={"post"})
def delete(remote_type: str, remote_id: str):
    controller.delete(remote_type=remote_type, remote_id=remote_id)
    return htmx.refresh()


@bp.route("/remotes/<string:remote_type>/<string:remote_id>/-/restore", methods={"post"})
def restore(remote_type: str, remote_id: str):
    controller.restore(remote_type=remote_type, remote_id=remote_id)
    return htmx.refresh()


@bp.route("/remotes/<string:remote_type>/<string:remote_id>/-/permanently-delete", methods={"post"})
def permanently_delete(remote_type: str, remote_id: str):
    controller.permanently_delete(remote_type=remote_type, remote_id=remote_id)
    return htmx.refresh()


@bp.route("/remotes/-/search/<remote_type:remote_type>")
def search_source(remote_type: typing.Type[Remote]):
    query = flask.request.args.get("query", default="", type=str)

    candidate_work_id = flask.request.args.get("work_id", type=uuid.UUID)
    candidate_work: Work | None
    if candidate_work_id:
        candidate_work = db.session.get(Work, candidate_work_id)
        candidate_work_details = candidate_work.resolve_details()
        query = query or candidate_work_details.title
    else:
        candidate_work = None

    remote_items = controller.managers[remote_type.remote_type()].search(query) if query else Pagination.empty()

    return render(RemoteSearchPage(remote_type=remote_type, candidate_work=candidate_work, remote_items=remote_items))
    # return flask.render_template(
    #     [f"remote/{remote_type}/search.html", "remote/search.html"],
    #     remote_type=remote_type,
    #     remote_info=self.managers[remote_type].remote_type.info,
    #     work=candidate_work,
    #     query=query,
    #     items=remote_items,
    # )


@bp.route("/works/<uuid:work_id>/-/link-work", methods={"post"})
def link_work(work_id: uuid.UUID):
    remote_type = flask.request.args["remote_type"]
    remote_id = flask.request.args["remote_id"]

    work = controller.link_work(work_id=work_id, remote_type=remote_type, remote_id=remote_id)
    return htmx.redirect(work.url_for())
