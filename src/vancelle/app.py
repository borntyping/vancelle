import pathlib
import typing

import flask
import flask.templating
import frozendict
import svcs.flask

from vancelle.blueprints.board import bp as bp_board
from .blueprints.data import bp as bp_data
from .blueprints.entry import bp as bp_entry
from .blueprints.errors import bp as bp_errors
from .blueprints.health import bp as bp_health
from .blueprints.home import bp as bp_home
from .blueprints.record import bp as bp_record
from .blueprints.source import bp as bp_source
from .blueprints.user import bp as bp_user
from .blueprints.work import bp as bp_works
from .clients.client import HttpClientBuilder
from .clients.goodreads.http import GoodreadsPublicScraper
from .clients.images.client import ImageCache
from .clients.openlibrary.client import OpenLibraryAPI
from .clients.royalroad.client import RoyalRoadScraper
from .clients.steam.client_store_api import SteamStoreAPI
from .clients.steam.client_web_api import SteamWebAPI
from .clients.tmdb.client import TmdbAPI
from .ext.structlog import configure_logging
from .extensions import alembic, cors, db, htmx, login_manager, sentry

root = pathlib.Path(__file__).parent


class VancelleFlask(flask.Flask):
    def create_jinja_environment(self) -> flask.templating.Environment:
        return NotImplemented


def create_app(config: typing.Mapping[str, typing.Any] = frozendict.frozendict(), /) -> flask.Flask:
    configure_logging()

    app = VancelleFlask("vancelle")
    app.config["ALEMBIC"] = {
        "script_location": (root / "migrations").as_posix(),
    }
    app.config["ALEMBIC_CONTEXT"] = {
        "alembic_module_prefix": "alembic.op.",
        "sqlalchemy_module_prefix": "sqlalchemy.",
    }
    app.config["SQLALCHEMY_RECORD_QUERIES"] = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["REMEMBER_COOKIE_SAMESITE"] = "Lax"
    app.config.from_mapping(config)
    app.config.from_prefixed_env("VANCELLE")

    if default := app.config.get("SQLALCHEMY_ENGINES_DEFAULT"):
        app.config["SQLALCHEMY_ENGINES"] = {"default": default}

    svcs.flask.init_app(app)
    svcs.flask.register_value(app, flask.Flask, app)
    svcs.flask.register_factory(app, HttpClientBuilder, HttpClientBuilder.factory)
    svcs.flask.register_factory(app, GoodreadsPublicScraper, GoodreadsPublicScraper.factory)
    svcs.flask.register_factory(app, ImageCache, ImageCache.factory)
    svcs.flask.register_factory(app, OpenLibraryAPI, OpenLibraryAPI.factory)
    svcs.flask.register_factory(app, RoyalRoadScraper, RoyalRoadScraper.factory)
    svcs.flask.register_factory(app, SteamStoreAPI, SteamStoreAPI.factory)
    svcs.flask.register_factory(app, SteamWebAPI, SteamWebAPI.factory)
    svcs.flask.register_factory(app, TmdbAPI, TmdbAPI.factory)

    alembic.init_app(app)
    cors.init_app(app)
    db.init_app(app)
    htmx.init_app(app)
    login_manager.init_app(app)
    sentry.init_app(app)

    app.register_blueprint(bp_board)
    app.register_blueprint(bp_errors)
    app.register_blueprint(bp_health)
    app.register_blueprint(bp_home)
    app.register_blueprint(bp_data)
    app.register_blueprint(bp_user)

    app.register_blueprint(bp_works)
    app.register_blueprint(bp_record)
    app.register_blueprint(bp_entry)
    app.register_blueprint(bp_source)

    return app
