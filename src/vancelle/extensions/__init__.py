import flask_alembic
import flask_cors
import flask_login
import flask_sqlalchemy_lite

from .htmx import HtmxExtension
from .sentry import SentryExtension
from ..models import Base

alembic = flask_alembic.Alembic(metadatas=Base.metadata, run_mkdir=False)
db = flask_sqlalchemy_lite.SQLAlchemy(session_options={"expire_on_commit": False})

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
login_manager = flask_login.LoginManager()

htmx = HtmxExtension()
sentry = SentryExtension()
