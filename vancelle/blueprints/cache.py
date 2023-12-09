import flask
import flask_login
import structlog

from vancelle.controllers.cache import CacheController

logger = structlog.get_logger(logger_name=__name__)

controller = CacheController()
bp = flask.Blueprint("cache", __name__, url_prefix="/cache", template_folder="templates")
bp.cli.short_help = "Manage caches."


@bp.before_request
@flask_login.login_required
def before_request():
    pass


@bp.route("/")
def index():
    return flask.render_template("cache.html")


@bp.route("/-/clear-request-cache")
def clear_request_cache():
    controller.clear_request_cache()
    return flask.redirect(flask.url_for(".index"))


@bp.route("/-/reload-steam-cache")
def reload_steam_cache():
    controller.reload_steam_cache()
    return flask.redirect(flask.url_for(".index"))


@bp.cli.command("clear-requests-cache")
def cli_clear_requests_cache():
    controller.clear_request_cache()


@bp.cli.command("reload-steam-cache")
def cli_reload_steam_cache():
    controller.reload_steam_cache()
