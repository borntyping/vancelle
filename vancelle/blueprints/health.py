import flask

bp = flask.Blueprint("health", __name__, url_prefix="/health")


@bp.route("/ready")
def ready():
    return flask.Response()
