import pathlib

import flask_cors
import flask_debugtoolbar
import flask_login
import flask_migrate
import flask_sqlalchemy

from .ext_apis import ApisExtension
from .ext_html import HtmlExtension
from .ext_htmx import HtmxExtension
from .ext_sentry import SentryExtension
from ..models import Base

cors = flask_cors.CORS(
    allow_headers=[
        *HtmxExtension.CORS_ALLOW_HEADERS,
        *SentryExtension.CORS_ALLOW_HEADERS,
    ],
    expose_headers=[
        *HtmxExtension.CORS_EXPOSE_HEADERS,
        *SentryExtension.CORS_EXPOSE_HEADERS,
    ],
)
db = flask_sqlalchemy.SQLAlchemy(model_class=Base, session_options={"expire_on_commit": False})
debug_toolbar = flask_debugtoolbar.DebugToolbarExtension()
login_manager = flask_login.LoginManager()
migrate = flask_migrate.Migrate(
    directory=pathlib.Path(__file__).parent.with_name("migrations"),
    alembic_module_prefix="alembic.op.",
    sqlalchemy_module_prefix="sqlalchemy.",
)
sentry = SentryExtension()

apis = ApisExtension()
html = HtmlExtension()
htmx = HtmxExtension()
