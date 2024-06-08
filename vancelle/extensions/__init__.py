import flask_alembic
import flask_cors
import flask_debugtoolbar
import flask_login
import flask_sqlalchemy_lite

from .ext_html import HtmlExtension
from .ext_htmx import HtmxExtension

alembic = flask_alembic.Alembic(run_mkdir=False)
db = flask_sqlalchemy_lite.SQLAlchemy(session_options={"expire_on_commit": False})

cors = flask_cors.CORS(
    allow_headers=[
        *HtmxExtension.CORS_ALLOW_HEADERS,
    ],
    expose_headers=[
        *HtmxExtension.CORS_EXPOSE_HEADERS,
    ],
)
debug_toolbar = flask_debugtoolbar.DebugToolbarExtension()
login_manager = flask_login.LoginManager()

html = HtmlExtension()
htmx = HtmxExtension()
