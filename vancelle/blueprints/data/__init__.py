import flask
import flask_login

from .goodreads import bp as bp_goodreads
from .notion import bp as bp_notion

bp = flask.Blueprint("data", __name__)
bp.cli.short_help = "Import and export data."

bp.register_blueprint(bp_goodreads)
bp.register_blueprint(bp_notion)


@bp.before_request
@flask_login.login_required
def before_request():
    pass
