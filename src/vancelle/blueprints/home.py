import flask
import flask_login

from vancelle.html.vancelle.pages.home import HomePage
from vancelle.lib.heavymetal import render

bp = flask.Blueprint("home", __name__)


@bp.route("/")
@flask_login.login_required
def home():
    return render(HomePage())


@bp.route("/favicon.ico")
def favicon():
    return flask.send_from_directory(flask.current_app.static_folder, "favicon/favicon.ico")
