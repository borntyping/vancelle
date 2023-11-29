import flask
import flask.sansio.blueprints
import structlog
import werkzeug.exceptions

from vancelle.exceptions import ApplicationError
from vancelle.extensions import htmx

logger = structlog.get_logger(logger_name=__name__)

bp = flask.Blueprint("errors", __name__, url_prefix="/errors", template_folder="templates")


@bp.record_once
def once(state: flask.sansio.blueprints.BlueprintSetupState):
    state.app.register_error_handler(ApplicationError, application_error_handler)
    state.app.register_error_handler(werkzeug.exceptions.HTTPException, http_error_handler)
    state.app.register_error_handler(Exception, generic_error_handler)


def application_error_handler(notification: ApplicationError):
    if htmx:
        return flask.Response(
            flask.render_template(
                "toast.html",
                title="Warning",
                body=f"{notification}",
                text_classes="has-text-warning",
                toast_classes="is-warning",
            ),
            headers={"HX-Reswap": "none"},
        )

    return flask.render_template("error.html", exception=notification)


def http_error_handler(exception: werkzeug.exceptions.HTTPException):
    response = exception.get_response()
    response.data = flask.render_template("http_error.html", exception=exception)
    return response


def generic_error_handler(exception: Exception):
    """
    https://flask.palletsprojects.com/en/2.3.x/errorhandling/#generic-exception-handlers
    """
    if isinstance(exception, werkzeug.exceptions.HTTPException):
        return exception

    logger.error("Unhandled exception", exc_info=exception)

    if htmx:
        return flask.Response(
            flask.render_template(
                "toast.html",
                title="Error",
                body=f"{exception.__class__.__qualname__}: {exception}",
                text_classes="has-text-danger",
                toast_classes="is-danger",
            ),
            headers={"HX-Reswap": "none"},
        )

    if flask.current_app.config["DEBUG"]:
        raise exception

    return flask.render_template("error.html", exception=exception)
