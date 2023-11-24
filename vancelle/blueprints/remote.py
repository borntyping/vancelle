import uuid

import flask
import flask_login

from ..controllers.remote import RemotesController
from ..extensions import htmx
from ..extensions.ext_html import Toggle
from ..models import Remote

controller = RemotesController()

bp = flask.Blueprint("remote", __name__)


@bp.before_request
@flask_login.login_required
def before_request():
    pass


@bp.route("/remotes/")
def index():
    remote_type = Toggle.from_request({k: v.full_noun for k, v in Remote.sources().items()}, "remote_type")

    remotes = controller.index(remote_type=remote_type.value)
    return flask.render_template("remote/index.html", remotes=remotes, remote_type=remote_type)


@bp.route("/remotes/<string:remote_type>/<string:remote_id>")
def detail(remote_type: str, remote_id: str):
    work_id = flask.request.args.get("work_id", type=uuid.UUID)

    return controller.render_detail(remote_type=remote_type, remote_id=remote_id, work_id=work_id)


@bp.route("/remotes/<string:remote_type>/<string:remote_id>/-/create-work", methods={"post"})
def create_work(remote_type: str, remote_id: str):
    work = controller.create_work(remote_type=remote_type, remote_id=remote_id, user=flask_login.current_user)
    return htmx.redirect(work.url_for())


@bp.route("/sources/<string:remote_type>/")
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


@bp.route("/works/<uuid:work_id>/remotes/<string:remote_type>/-/refresh", methods={"post"})
def refresh(work_id: uuid.UUID, remote_type: str):
    controller.refresh(work_id=work_id, remote_type=remote_type)
    return htmx.refresh()


@bp.route("/works/<uuid:work_id>/remotes/<string:remote_type>/-/delete", methods={"post"})
def delete(work_id: uuid.UUID, remote_type: str):
    controller.delete(work_id=work_id, remote_type=remote_type)
    return htmx.refresh()


@bp.route("/works/<uuid:work_id>/remotes/<string:remote_type>/-/restore", methods={"post"})
def restore(work_id: uuid.UUID, remote_type: str):
    controller.restore(work_id=work_id, remote_type=remote_type)
    return htmx.refresh()


@bp.route("/works/<uuid:work_id>/remotes/<string:remote_type>/-/permanently-delete", methods={"post"})
def permanently_delete(work_id: uuid.UUID, remote_type: str):
    controller.permanently_delete(work_id=work_id, remote_type=remote_type)
    return htmx.refresh()
