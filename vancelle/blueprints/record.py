import uuid

import flask
import flask.views
import flask_login
import structlog
from flask_wtf import FlaskForm
from wtforms import DateField, TextAreaField
from wtforms.validators import Length, Optional

from vancelle.controllers.record import RecordController
from vancelle.extensions import db, htmx

logger = structlog.get_logger(logger_name=__name__)
controller = RecordController()
bp = flask.Blueprint("records", __name__, url_prefix="/<uuid:work_id>/records")


@bp.before_request
@flask_login.login_required
def before_request():
    pass


class RecordForm(FlaskForm):
    date_started = DateField("Started", validators=[Optional()])
    date_stopped = DateField("Stopped", validators=[Optional()])
    notes = TextAreaField("Notes", validators=[Optional(), Length(max=256)])


@bp.route("/", methods=["POST"])
def create(work_id: uuid.UUID):
    started_today = flask.request.args.get("started_today", default=False, type=bool)
    stopped_today = flask.request.args.get("stopped_today", default=False, type=bool)
    record = controller.create(work_id, started_today=started_today, stopped_today=stopped_today)
    return htmx.redirect(record.url_for())


@bp.route("/<uuid:record_id>/", methods={"GET", "POST"})
def detail(work_id: uuid.UUID, record_id: uuid.UUID):
    record = controller.get_or_404(user_id=flask_login.current_user.id, work_id=work_id, record_id=record_id)
    form = RecordForm(obj=record)

    if form.validate_on_submit():
        form.populate_obj(record)
        db.session.add(record)
        db.session.commit()
        return flask.redirect(flask.url_for("work.detail", work_id=record.work_id))

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
