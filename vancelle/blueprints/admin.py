import flask
import flask_login
import structlog

from vancelle.controllers.admin import AdminController

logger = structlog.get_logger(logger_name=__name__)

controller = AdminController()
bp = flask.Blueprint("admin", __name__, url_prefix="/admin", template_folder="templates")
bp.cli.short_help = "Setup and teardown the Postgres database."


@bp.before_request
@flask_login.login_required
def before_request():
    pass


@bp.route("/")
def index():
    return flask.render_template("admin.html")


@bp.route("/-/clear-request-cache")
def clear_request_cache():
    controller.clear_request_cache()
    return flask.redirect(flask.url_for(".index"))


@bp.cli.command("create-database")
def cli_create_database():
    """Create the database schema."""
    controller.create_database()


@bp.cli.command("reset-database")
def cli_reset_database():
    """Drop all tables in the database and create them again."""
    controller.drop_database()
    controller.create_database()


@bp.cli.command("clear-requests-cache")
def cli_clear_requests_cache():
    controller.clear_request_cache()
