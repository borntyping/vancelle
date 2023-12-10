import flask
import flask_login
import structlog

from vancelle.blueprints.goodreads import bp as bp_goodreads

logger = structlog.get_logger(logger_name=__name__)

bp = flask.Blueprint("data", __name__)
bp.cli.short_help = "Import and export data."

bp.register_blueprint(bp_goodreads)


@bp.before_request
@flask_login.login_required
def before_request():
    pass


@bp.cli.command("migrate")
def migrate():
    """Run temporary data migrations."""
    pass
