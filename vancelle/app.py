import os
import typing
import wsgiref.types

import flask
import svcs.flask

from .blueprints.bulma import bp as bp_bulma
from .blueprints.data import bp as bp_data
from .blueprints.errors import bp as bp_errors
from .blueprints.health import bp as bp_health
from .blueprints.home import bp as bp_home
from .blueprints.record import bp as bp_record
from .blueprints.remote import bp as bp_remote
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
from .extensions import cors, db, debug_toolbar, html, htmx, login_manager, migrate
from .shelf import Shelf


def create_app(config: typing.Mapping[str, typing.Any], /) -> flask.Flask:
    app = flask.Flask("vancelle")
    app.config["SQLALCHEMY_RECORD_QUERIES"] = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
    app.config["REMEMBER_COOKIE_SAMESITE"] = "Lax"
    app.config.from_mapping(config)
    app.config.from_prefixed_env("VANCELLE")

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

    cors.init_app(app)
    db.init_app(app)
    debug_toolbar.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    html.init_app(app)
    htmx.init_app(app)

    app.register_blueprint(bp_bulma)
    app.register_blueprint(bp_errors)
    app.register_blueprint(bp_health)
    app.register_blueprint(bp_home)
    app.register_blueprint(bp_data)
    app.register_blueprint(bp_user)

    app.register_blueprint(bp_works)
    app.register_blueprint(bp_record)
    app.register_blueprint(bp_remote)

    return app


def create_app_once(config: typing.Mapping[str, typing.Any], /) -> flask.Flask:
    configure_logging()
    return create_app(config)


def create_personal_app() -> wsgiref.types.WSGIApplication:
    config: dict[str, typing.Any] = {
        "GOODREADS_SHELF_MAPPING": {
            "currently-reading": Shelf.PLAYING,
            "gave-up-on": Shelf.ABANDONED,
            "non-fiction": Shelf.PAUSED,
            "read": Shelf.COMPLETED,
            "to-read": Shelf.UPCOMING,
            "to-read-maybe": Shelf.UNDECIDED,
            "to-read-non-fiction": Shelf.SHELVED,
            "to-read-sequels": Shelf.UPCOMING,
        },
        "SENTRY_ENABLED": True,
        "SPOTLIGHT_ENABLED": True,
    }

    if database_url := os.environ.get("DATABASE_URL"):
        config["SQLALCHEMY_DATABASE_URI"] = database_url

    return create_app_once(config)
