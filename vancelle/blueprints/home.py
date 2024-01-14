import flask

bp = flask.Blueprint("home", __name__)


@bp.route("/favicon.ico")
def favicon():
    return flask.send_from_directory(flask.current_app.static_folder, "favicon/favicon.ico")
