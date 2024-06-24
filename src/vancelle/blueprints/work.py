import uuid

import flask.sansio.blueprints
import flask_login
import structlog
import svcs
import werkzeug.exceptions

from vancelle.clients.images.client import ImageCache
from vancelle.controllers.source import SourceController
from vancelle.controllers.work import WorkController
from vancelle.exceptions import ApplicationError
from vancelle.extensions import db, htmx
from vancelle.forms.work import WorkForm, WorkIndexArgs, WorkShelfForm
from vancelle.html.vancelle.pages.work import work_create_page, work_detail_page, work_index_page, work_update_page
from vancelle.lib.heavymetal import render
from vancelle.models.work import Work

logger = structlog.get_logger(logger_name=__name__)

controller = WorkController()
source_controller = SourceController()

bp = flask.Blueprint("work", __name__, url_prefix="/works")


@bp.before_request
@flask_login.login_required
def before_request():
    pass


@bp.route("/-/create", methods={"get", "post"})
def create():
    form = WorkForm()

    if form.validate_on_submit():
        work = Work(id=uuid.uuid4(), user=flask_login.current_user)
        form.populate_obj(work)
        db.session.add(work)
        db.session.commit()
        return flask.redirect(work.url_for())

    return render(work_create_page(work_form=form))


@bp.route("/")
def index():
    work_index_args = WorkIndexArgs(formdata=flask.request.args)
    works = work_index_args.paginate()

    return render(work_index_page(works, work_index_args))


@bp.route("/<uuid:work_id>")
def detail(work_id: uuid.UUID):
    work = controller.get_or_404(work_id)
    work_shelf_form = WorkShelfForm(obj=work)
    return render(work_detail_page(work=work, work_shelf_form=work_shelf_form))


@bp.route("/<uuid:work_id>/cover")
def cover(work_id: uuid.UUID):
    images = svcs.flask.get(ImageCache)
    work = controller.get_or_404(work_id)
    if not work.cover:
        raise werkzeug.exceptions.NotFound("Work has no cover image.")
    return images.as_response(work.cover)


@bp.route("/<uuid:work_id>/background")
def background(work_id: uuid.UUID):
    images = svcs.flask.get(ImageCache)
    work = controller.get_or_404(work_id)
    if not work.background:
        raise werkzeug.exceptions.NotFound("Work has no background image.")
    return images.as_response(work.background)


@bp.route("/<uuid:work_id>/-/shelve", methods={"post"})
def shelve(work_id: uuid.UUID):
    work = controller.get_or_404(work_id)
    work_shelf_form = WorkShelfForm(obj=work)

    if work_shelf_form.validate_on_submit():
        work_shelf_form.populate_obj(work)
        db.session.commit()
        flask.flash(f"Moved {work.resolve_details().title} to the {work.shelf.title} shelf.", "Shelved work")
        return htmx.refresh()

    raise ApplicationError(work_shelf_form.errors)


@bp.route("/<uuid:work_id>/-/update", methods={"get", "post"})
def update(work_id: uuid.UUID):
    work = controller.get_or_404(work_id)
    work_form = WorkForm(obj=work)

    if work_form.validate_on_submit():
        work_form.populate_obj(work)
        db.session.commit()
        return htmx.redirect(work.url_for())

    return render(work_update_page(work, work_form))


@bp.route("/<uuid:work_id>/-/delete", methods={"post"})
def delete(work_id: uuid.UUID):
    controller.delete(controller.get_or_404(work_id))
    return htmx.refresh()


@bp.route("/<uuid:work_id>/-/restore", methods={"post"})
def restore(work_id: uuid.UUID):
    controller.restore(controller.get_or_404(work_id))
    return htmx.refresh()


@bp.route("/<uuid:work_id>/-/permanently-delete", methods={"post"})
def permanently_delete(work_id: uuid.UUID):
    controller.permanently_delete(controller.get_or_404(work_id))
    return htmx.redirect(flask.url_for(".index"))
