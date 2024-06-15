import flask
import flask_login

from vancelle.html.vancelle.pages.home import HomePage

bp = flask.Blueprint("home", __name__)


@bp.route("/")
@flask_login.login_required
def home():
    return HomePage().render()


@bp.route("/favicon.ico")
def favicon():
    return flask.send_from_directory(flask.current_app.static_folder, "favicon/favicon.ico")
