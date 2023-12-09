import flask_cors
import flask_debugtoolbar
import flask_login
import flask_sqlalchemy

from .ext_apis import ApisExtension
from .ext_html import HtmlExtension
from .ext_htmx import HtmxExtension
from ..models import Base

cors = flask_cors.CORS()
db = flask_sqlalchemy.SQLAlchemy(model_class=Base, session_options={"expire_on_commit": False})
debug_toolbar = flask_debugtoolbar.DebugToolbarExtension()
login_manager = flask_login.LoginManager()

apis = ApisExtension()
htmx = HtmxExtension()
html = HtmlExtension()
