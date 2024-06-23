import uuid

import flask
import flask.views
import flask_login
import structlog
from werkzeug.exceptions import BadRequest

from vancelle.controllers.record import RecordController
from vancelle.extensions import db, htmx
from vancelle.forms.record import RecordForm
from vancelle.html.vancelle.pages.record import record_update_page
from vancelle.lib.heavymetal import render
from vancelle.models.record import RelativeDate

logger = structlog.get_logger(logger_name=__name__)
controller = RecordController()
bp = flask.Blueprint("record", __name__, url_prefix="/records")


@bp.before_request
@flask_login.login_required
def before_request():
    pass


@bp.route("/-/create", methods={"get", "post"})
def create():
    """TODO: record_create_page, matching work_create_page."""

    work_id = flask.request.args.get("work_id", type=uuid.UUID)
    started = flask.request.args.get("started", type=RelativeDate)
    stopped = flask.request.args.get("stopped", type=RelativeDate)

    if work_id is None:
        raise BadRequest()

    record = controller.create(work_id, started=started, stopped=stopped)
    return htmx.redirect(record.url_for())


@bp.route("/<uuid:record_id>/", methods={"GET", "POST"})
def detail(record_id: uuid.UUID):
    record = controller.select(record_id)
    record_form = RecordForm(obj=record)

    if record_form.validate_on_submit():
        if record_form.date_sync.data is True:
            record_form.date_stopped.data = record_form.date_started.data

        record_form.populate_obj(record)
        db.session.add(record)
        db.session.commit()
        return htmx.redirect(record.work.url_for())

    if htmx and record_form.errors:
        raise BadRequest()

    return render(record_update_page(record=record, record_form=record_form))


@bp.route("/<uuid:record_id>/-/update", methods=["POST"])
def start_today(record_id: uuid.UUID):
    started = flask.request.args.get("started", type=RelativeDate)
    stopped = flask.request.args.get("stopped", type=RelativeDate)
    controller.update(record_id, started=started, stopped=stopped)
    return htmx.refresh()


@bp.route("/<uuid:record_id>/-/delete", methods=["POST"])
def delete(record_id: uuid.UUID):
    controller.delete(record_id)
    return htmx.refresh()


@bp.route("/<uuid:record_id>/-/restore", methods=["POST"])
def restore(record_id: uuid.UUID):
    controller.restore(record_id)
    return htmx.refresh()


@bp.route("/<uuid:record_id>/", methods=["DELETE"])
@bp.route("/<uuid:record_id>/-/permanently-delete", methods=["POST"])
def permanently_delete(record_id: uuid.UUID):
    record = controller.permanently_delete(record_id)
    return htmx.redirect(record.work.url_for())
