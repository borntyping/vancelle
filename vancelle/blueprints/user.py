import uuid

import click
import flask
import flask_login
import flask_wtf.file
import sqlalchemy
import sqlalchemy.exc
import sqlalchemy.orm
import structlog
import werkzeug.security
import werkzeug.exceptions
import wtforms

from vancelle.controllers.user import UserController
from vancelle.ext.flask_login import get_user
from vancelle.extensions import db, login_manager
from vancelle.models import User

logger = structlog.get_logger(logger_name=__name__)

BACKUP_FILENAME = "vancelle-backup.json"

controller = UserController()
bp = flask.Blueprint("user", __name__)
bp.cli.short_help = "Manage users."


class LoginForm(flask_wtf.FlaskForm):
    username = wtforms.StringField("Username")
    password = wtforms.PasswordField("Password")


class ImportForm(flask_wtf.FlaskForm):
    backup = flask_wtf.file.FileField("Backup", validators=[flask_wtf.file.FileRequired()])


@bp.app_errorhandler(werkzeug.exceptions.Unauthorized)
@bp.route("/user/login", methods={"get", "post"})
def login(exception: werkzeug.exceptions.Unauthorized | None = None):
    form = LoginForm()

    if not form.validate_on_submit():
        return flask.render_template("login.html", form=form, exception=exception)

    try:
        user = db.session.execute(sqlalchemy.select(User).filter_by(username=form.username.data)).scalar_one()
    except sqlalchemy.exc.NoResultFound:
        form.username.errors.append("Unknown username")
        return flask.render_template("login.html", form=form, exception=exception)

    if not werkzeug.security.check_password_hash(user.password, form.password.data):
        form.password.errors.append("Incorrect password")
        return flask.render_template("login.html", form=form, exception=exception)

    flask_login.login_user(user, remember=True)
    flask.flash(f"Logged in as {user.username}", "Logged in")
    return flask.redirect(flask.url_for("work.index"))


@bp.route("/user/logout")
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for("work.index"))


@bp.route("/user/profile")
@bp.route("/user/import", methods={"post"}, endpoint="import")
def profile():
    form = ImportForm()

    if form.validate_on_submit():
        controller.import_json(form.backup.data.read(), user=flask_login.current_user)
        return flask.redirect(flask.url_for("user.profile"))

    work_count = flask_login.current_user.works.count()
    return flask.render_template(
        "user/profile.html",
        form=form,
        work_count=work_count,
        filename=BACKUP_FILENAME,
    )


@bp.route("/user/export")
def export():
    return flask.Response(
        controller.export_json(user=flask_login.current_user),
        mimetype="application/json",
        headers={"Content-Disposition": f'attachment; filename="{BACKUP_FILENAME}"'},
    )


@bp.route("/users/")
@flask_login.login_required
def index():
    users = db.paginate(
        sqlalchemy.select(User).order_by(User.username).options(sqlalchemy.orm.load_only(User.id, User.username))
    )
    return flask.render_template("user/index.html", users=users)


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, user_id)


@bp.cli.command("create")
@click.option("--id", type=click.UUID, default=uuid.uuid4, required=True)
@click.option("--username", prompt=True, required=True)
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, required=True)
def cli_create_user(id: uuid.UUID, username: str, password: str):
    """Create a new user. You'll need this before you can login for the first time."""
    user = User(id=id, username=username, password=werkzeug.security.generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    logger.warning("Created user", user=user)


@bp.cli.command("clear")
@click.option("--username", required=True)
def cli_clear_user(username: str) -> None:
    user = get_user(username)
    for work in user.works:
        db.session.delete(work)
    db.session.commit()
