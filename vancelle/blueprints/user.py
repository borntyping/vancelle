import uuid

import click
import flask
import flask_login
import flask_wtf
import sqlalchemy
import sqlalchemy.exc
import structlog
import wtforms
import werkzeug.security
from sqlalchemy import select
from sqlalchemy.orm import load_only

from vancelle.models import User
from vancelle.extensions import db, login_manager

logger = structlog.get_logger(logger_name=__name__)

bp = flask.Blueprint("user", __name__, url_prefix="/users")
bp.cli.short_help = "Manage users."


class LoginForm(flask_wtf.FlaskForm):
    username = wtforms.StringField("Username")
    password = wtforms.PasswordField("Password")


@bp.route("/login", methods={"get", "post"})
def login():
    form = LoginForm()

    if not form.validate_on_submit():
        return flask.render_template("login.html", form=form)

    try:
        user = db.session.execute(sqlalchemy.select(User).filter_by(username=form.username.data)).scalar_one()
    except sqlalchemy.exc.NoResultFound:
        form.username.errors.append("Unknown username")
        return flask.render_template("login.html", form=form)

    if not werkzeug.security.check_password_hash(user.password, form.password.data):
        form.password.errors.append("Incorrect password")
        return flask.render_template("login.html", form=form)

    flask_login.login_user(user, remember=True)
    flask.flash(f"Logged in as {user.username}", "Logged in")
    return flask.redirect(flask.url_for("work.index"))


@bp.route("/logout")
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for("work.index"))


@bp.route("/")
@flask_login.login_required
def index():
    users = db.paginate(select(User).order_by(User.username).options(load_only(User.id, User.username)))
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
