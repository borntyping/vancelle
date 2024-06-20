import uuid

import flask
import flask.views
import flask_login
import structlog
from flask_wtf import FlaskForm
from werkzeug.exceptions import BadRequest
from wtforms import DateField, BooleanField, StringField
from wtforms.validators import Length, Optional

from vancelle.controllers.record import RecordController
from vancelle.ext.wtforms import NoneFilter
from vancelle.extensions import db, htmx

logger = structlog.get_logger(logger_name=__name__)
controller = RecordController()
bp = flask.Blueprint("record", __name__, url_prefix="/<uuid:work_id>/records")


@bp.before_request
@flask_login.login_required
def before_request():
    pass


class RecordForm(FlaskForm):
    date_started = DateField("Started", validators=[Optional()])
    date_stopped = DateField("Stopped", validators=[Optional()])
    date_sync = BooleanField("Use start date for end date", default=False)
    notes = StringField("Bookmark", validators=[Optional(), Length(max=256)], filters=[NoneFilter()])


@bp.route("/-/new", methods=["POST"])
def new(work_id: uuid.UUID):
    record = controller.create(work_id)
    return htmx.redirect(record.url_for())


@bp.route("/-/new-started-today", methods=["POST"])
def new_started_today(work_id: uuid.UUID):
    controller.create(work_id, started_today=True)
    return htmx.refresh()


@bp.route("/-/new-stopped-today", methods=["POST"])
def new_stopped_today(work_id: uuid.UUID):
    controller.create(work_id, stopped_today=True)
    return htmx.refresh()


@bp.route("/<uuid:record_id>/", methods={"GET", "POST"})
def detail(work_id: uuid.UUID, record_id: uuid.UUID):
    record = controller.get_or_404(user_id=flask_login.current_user.id, work_id=work_id, record_id=record_id)
    form = RecordForm(obj=record)

    if form.validate_on_submit():
        if form.date_sync.data is True:
            form.date_stopped.data = form.date_started.data

        form.populate_obj(record)
        db.session.add(record)
        db.session.commit()
        return htmx.redirect(flask.url_for("work.detail", work_id=record.work_id))

    if htmx and form.errors:
        raise BadRequest()

    return flask.render_template("record/detail.html", record=record, form=form)


@bp.route("/<uuid:record_id>/-/start-today", methods=["POST"])
def start_today(work_id: uuid.UUID, record_id: uuid.UUID):
    controller.start_today(work_id, record_id)
    return htmx.refresh()


@bp.route("/<uuid:record_id>/-/finish-today", methods=["POST"])
def stop_today(work_id: uuid.UUID, record_id: uuid.UUID):
    controller.stop_today(work_id, record_id)
    return htmx.refresh()


@bp.route("/<uuid:record_id>/-/delete", methods=["POST"])
def delete(work_id: uuid.UUID, record_id: uuid.UUID):
    controller.delete(work_id, record_id)
    return htmx.refresh()


@bp.route("/<uuid:record_id>/-/restore", methods=["POST"])
def restore(work_id: uuid.UUID, record_id: uuid.UUID):
    controller.restore(work_id, record_id)
    return htmx.refresh()


@bp.route("/<uuid:record_id>/", methods=["DELETE"])
@bp.route("/<uuid:record_id>/-/permanently-delete", methods=["POST"])
def permanently_delete(work_id: uuid.UUID, record_id: uuid.UUID):
    record = controller.permanently_delete(work_id, record_id)
    return htmx.redirect(record.work.url_for())
