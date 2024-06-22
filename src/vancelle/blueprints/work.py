import uuid

import flask.sansio.blueprints
import flask_login
import structlog
import svcs
import werkzeug.exceptions

from vancelle.clients.images.client import ImageCache
from vancelle.controllers.work import WorkController, WorkQuery
from vancelle.exceptions import ApplicationError
from vancelle.extensions import db, htmx
from vancelle.forms.work import WorkShelfForm, WorkForm, WorkIndexForm
from vancelle.html.vancelle.pages.work import work_create_page, work_detail_page, work_update_page
from vancelle.lib.heavymetal import render
from vancelle.models.work import Work

logger = structlog.get_logger(logger_name=__name__)

controller = WorkController()

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
    form = WorkIndexForm(formdata=flask.request.args, meta={"csrf": False})
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

    match form.layout.data:
        case "board":
            shelves, total = query.shelves()
            page = flask.render_template(
                "work/index_board.html",
                form=form,
                layout=form.layout.data,
                work_shelf=form.work_shelf.data,
                work_case=form.work_case.data,
                shelves=shelves,
                total=total,
            )
        case "list":
            works = query.paginate()
            page = flask.render_template(
                "work/index_list.html",
                form=form,
                layout=form.layout.data,
                works=works,
                total=works.count,
            )
        case _:
            raise werkzeug.exceptions.BadRequest(f"Unknown layout {form.layout.data!r}")

    response = flask.Response(page)
    response.delete_cookie("index")
    return response


@bp.route("/<uuid:work_id>")
def detail(work_id: uuid.UUID):
    work = controller.get_or_404(id=work_id)
    work_shelf_form = WorkShelfForm(obj=work)
    return render(work_detail_page(work=work, work_shelf_form=work_shelf_form))


@bp.route("/<uuid:work_id>/cover")
def cover(work_id: uuid.UUID):
    images = svcs.flask.get(ImageCache)
    work = controller.get_or_404(id=work_id)
    if not work.cover:
        raise werkzeug.exceptions.NotFound("Work has no cover image.")
    return images.as_response(work.cover)


@bp.route("/<uuid:work_id>/background")
def background(work_id: uuid.UUID):
    images = svcs.flask.get(ImageCache)
    work = controller.get_or_404(id=work_id)
    if not work.background:
        raise werkzeug.exceptions.NotFound("Work has no background image.")
    return images.as_response(work.background)


@bp.route("/<uuid:work_id>/-/shelve", methods={"post"})
def shelve(work_id: uuid.UUID):
    work = controller.get_or_404(id=work_id)
    work_shelf_form = WorkShelfForm(obj=work)

    if work_shelf_form.validate_on_submit():
        work_shelf_form.populate_obj(work)
        db.session.commit()
        flask.flash(f"Moved {work.resolve_details().title} to the {work.shelf.title} shelf.", "Shelved work")
        return htmx.refresh()

    raise ApplicationError(work_shelf_form.errors)


@bp.route("/<uuid:work_id>/-/update", methods={"get", "post"})
def update(work_id: uuid.UUID):
    work = controller.get_or_404(id=work_id)
    work_form = WorkForm(obj=work)

    if work_form.validate_on_submit():
        work_form.populate_obj(work)
        db.session.commit()
        return htmx.redirect(work.url_for())

    return render(work_update_page(work, work_form))


@bp.route("/<uuid:work_id>/-/delete", methods={"post"})
def delete(work_id: uuid.UUID):
    controller.delete(controller.get_or_404(id=work_id))
    return htmx.refresh()


@bp.route("/<uuid:work_id>/-/restore", methods={"post"})
def restore(work_id: uuid.UUID):
    controller.restore(controller.get_or_404(id=work_id))
    return htmx.refresh()


@bp.route("/<uuid:work_id>/-/permanently-delete", methods={"post"})
def permanently_delete(work_id: uuid.UUID):
    controller.permanently_delete(controller.get_or_404(id=work_id))
    return htmx.redirect(flask.url_for(".index"))
