import uuid

import flask
import flask_login
import svcs
from werkzeug.exceptions import NotFound

from ..clients.images.client import ImageCache
from ..controllers.remote import RemotesController
from ..extensions import htmx
from ..extensions.ext_html import Toggle
from ..models.remote import Remote

controller = RemotesController()

bp = flask.Blueprint("remote", __name__)


@bp.before_request
@flask_login.login_required
def before_request():
    pass


@bp.route("/remotes/")
def index():
    toggle_remote_type = Toggle({cls.remote_type(): cls.info.noun_full for cls in Remote.iter_subclasses()})
    remote_type = toggle_remote_type.from_request(key="remote_type")

    remotes = controller.index(remote_type=remote_type.value)
    return flask.render_template("remote/index.html", remotes=remotes, remote_type=remote_type)


@bp.route("/remotes/<string:remote_type>/<string:remote_id>")
def detail(remote_type: str, remote_id: str):
    work_id = flask.request.args.get("work_id", type=uuid.UUID)

    return controller.render_detail(remote_type=remote_type, remote_id=remote_id, work_id=work_id)


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


@bp.route("/remotes/-/search/<string:remote_type>")
def search_source(remote_type: str):
    query = flask.request.args.get("query", default="", type=str)
    work_id = flask.request.args.get("work_id", type=uuid.UUID)

    return controller.render_search(work_id=work_id, remote_type=remote_type, query=query)


@bp.route("/works/<uuid:work_id>/-/link-work", methods={"post"})
def link_work(work_id: uuid.UUID):
    remote_type = flask.request.args["remote_type"]
    remote_id = flask.request.args["remote_id"]

    work = controller.link_work(work_id=work_id, remote_type=remote_type, remote_id=remote_id)
    return htmx.redirect(work.url_for())
