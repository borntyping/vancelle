import os
import typing

import flask

from .blueprints.admin import bp as bp_admin
from .blueprints.bulma import bp as bp_bulma
from .blueprints.data import bp as bp_io
from .blueprints.errors import bp as bp_errors
from .blueprints.health import bp as bp_health
from .blueprints.record import bp as bp_record
from .blueprints.remote import bp as bp_remote
from .blueprints.user import bp as bp_user
from .blueprints.work import bp as bp_works
from .ext.structlog import configure_logging
from .extensions import apis, cors, db, debug_toolbar, html, htmx, login_manager, sentry
from .shelf import Shelf

configure_logging()


def create_app(config: typing.Mapping[str, typing.Any], /) -> flask.Flask:
    app = flask.Flask(__name__)
    app.config["SQLALCHEMY_RECORD_QUERIES"] = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config.from_mapping(config)
    app.config.from_prefixed_env("VANCELLE")

    cors.init_app(app)
    db.init_app(app)
    debug_toolbar.init_app(app)
    login_manager.init_app(app)
    sentry.init_app(app)

    apis.init_app(app)
    html.init_app(app)
    htmx.init_app(app)

    app.register_blueprint(bp_admin)
    app.register_blueprint(bp_bulma)
    app.register_blueprint(bp_errors)
    app.register_blueprint(bp_health)
    app.register_blueprint(bp_io)
    app.register_blueprint(bp_user)

    app.register_blueprint(bp_works)
    app.register_blueprint(bp_record)
    app.register_blueprint(bp_remote)

    return app


def create_personal_app() -> flask.Flask:
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
    }

    if database_url := os.environ.get("DATABASE_URL"):
        config["SQLALCHEMY_DATABASE_URI"] = database_url

    return create_app(config)
