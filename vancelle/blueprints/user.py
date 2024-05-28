import gzip
import uuid

import click
import flask
import flask_login
import hotmetal
import sqlalchemy
import sqlalchemy.exc
import sqlalchemy.orm
import structlog
import werkzeug.exceptions
import werkzeug.security

from vancelle.controllers.settings import ApplicationSettingsController, UserSettingsController
from vancelle.ext.flask_login import get_user
from vancelle.extensions import db, login_manager
from vancelle.forms.user import ImportForm, LoginForm
from vancelle.html.vancelle.pages.user import SettingsPage, login_page
from vancelle.models import User

logger = structlog.get_logger(logger_name=__name__)

BACKUP_FILENAME = "vancelle-backup.json.gz"

user_settings = UserSettingsController()
application_settings = ApplicationSettingsController()

bp = flask.Blueprint("user", __name__, url_prefix="/user")
bp.cli.short_help = "Manage users."


@bp.app_errorhandler(werkzeug.exceptions.Unauthorized)
@bp.route("/login", methods={"get", "post"})
def login(exception: werkzeug.exceptions.Unauthorized | None = None):
    form = LoginForm()

    if not form.validate_on_submit():
        return hotmetal.render(login_page(login_form=form))

    try:
        user = db.session.execute(sqlalchemy.select(User).filter_by(username=form.username.data)).scalar_one()
    except sqlalchemy.exc.NoResultFound:
        form.username.errors.append("Unknown username")
        return hotmetal.render(login_page(login_form=form))

    if not werkzeug.security.check_password_hash(user.password, form.password.data):
        form.password.errors.append("Incorrect password")
        return hotmetal.render(login_page(login_form=form))

    flask_login.login_user(user, remember=True)
    flask.flash(f"Logged in as {user.username}.", "Logged in")
    return flask.redirect(flask.url_for("work.index"))


@bp.route("/logout")
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for("work.index"))


@bp.route("/settings")
@bp.route("/import", methods={"post"}, endpoint="import")
def settings():
    form = ImportForm()

    if form.validate_on_submit():
        data = gzip.decompress(form.backup.data.read()).decode("utf-8")
        user_settings.import_json(data, user=flask_login.current_user)
        return flask.redirect(flask.url_for(flask.request.endpoint))

    work_count = flask_login.current_user.works.count()
    return hotmetal.render(
        SettingsPage(
            import_form=form,
            work_count=work_count,
            filename=BACKUP_FILENAME,
        )
    )


@bp.route("/export")
def export():
    data = user_settings.export_json(user=flask_login.current_user)
    return flask.Response(
        response=gzip.compress(data.encode("utf-8")),
        mimetype="application/x-gzip-compressed",
        headers={"Content-Disposition": f'attachment; filename="{BACKUP_FILENAME}"'},
    )


@bp.route("/reload-steam-cache")
def reload_steam_cache():
    application_settings.reload_steam_cache()
    return flask.redirect(flask.url_for(".settings"))


@bp.cli.command("reload-steam-cache")
def cli_reload_steam_cache():
    application_settings.reload_steam_cache()


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, user_id)


@bp.cli.command("create")
@click.option("--id", type=click.UUID, default=uuid.uuid4, required=True)
@click.option("--username", prompt=True, required=True)
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, required=True)
def cli_create_user(id: uuid.UUID, username: str, password: str):
    """
    Ensure a user exists.

    You'll need this before you can log in for the first time.

    This can be safely called multiple times, so you can use it in init containers.
    """

    if user := db.session.execute(sqlalchemy.select(User).filter_by(username=username)).scalar_one_or_none():
        if user.id == id and werkzeug.security.check_password_hash(user.password, password):
            logger.info("User already exists", user=user)
            raise click.exceptions.Exit(0)
        else:
            logger.error("User already exists and does not match", user=user)
            raise click.exceptions.Exit(1)
    else:
        user = User(id=id, username=username, password=werkzeug.security.generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        logger.warning("Created user", user=user)


@bp.cli.command("clear")
@click.option("--username", required=True)
def cli_clear_user(username: str) -> None:
    """Delete all works belonging to a user."""
    user = get_user(username)
    for work in user.works:
        db.session.delete(work)
    db.session.commit()
