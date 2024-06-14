import flask
import flask.sansio.blueprints
import structlog
import werkzeug.exceptions

from vancelle.exceptions import ApplicationError
from vancelle.extensions import htmx
from vancelle.html.vancelle.components.toast import toast_response
from vancelle.html.vancelle.pages.errors import debug_page, error_page
from vancelle.lib.heavymetal import render

logger = structlog.get_logger(logger_name=__name__)

bp = flask.Blueprint("errors", __name__, url_prefix="/errors")


@bp.record_once
def once(state: flask.sansio.blueprints.BlueprintSetupState):
    state.app.register_error_handler(ApplicationError, application_error_handler)
    state.app.register_error_handler(werkzeug.exceptions.HTTPException, http_error_handler)
    state.app.register_error_handler(Exception, generic_error_handler)


@bp.route("/")
def index() -> str:
    return render(debug_page())


@bp.route("/application")
def raise_application_error() -> flask.Response:
    raise ApplicationError("Hello world!")


@bp.route("/http")
def raise_http_error() -> flask.Response:
    raise werkzeug.exceptions.ImATeapot


@bp.route("/generic")
def raise_generic_error() -> flask.Response:
    raise Exception("Hello world!")


def application_error_handler(notification: ApplicationError):
    if htmx:
        content = render(toast_response(title="Warning", body=f"{notification}"))
        return flask.Response(content, headers={"HX-Reswap": "none"})

    return render(error_page(title=notification.__class__.__qualname__, description=str(notification)))


def http_error_handler(exception: werkzeug.exceptions.HTTPException):
    if htmx:
        content = render(toast_response(f"{exception.code} {exception.name}", exception.description))
        return flask.Response(content, headers={"HX-Reswap": "none"})

    response = exception.get_response()
    response.data = render(error_page(title=f"{exception.code} {exception.name}", description=exception.description))
    return response


def generic_error_handler(exception: Exception):
    """
    https://flask.palletsprojects.com/en/2.3.x/errorhandling/#generic-exception-handlers
    """
    if isinstance(exception, werkzeug.exceptions.HTTPException):
        return exception

    logger.error("Unhandled exception", exc_info=exception)

    if htmx:
        content = render(toast_response("Error", f"{exception.__class__.__qualname__}: {exception}"))
        return flask.Response(content, headers={"HX-Reswap": "none"})

    if flask.current_app.config["DEBUG"]:
        raise exception

    return render(error_page(title=exception.__class__.__qualname__, description=str(exception)))
