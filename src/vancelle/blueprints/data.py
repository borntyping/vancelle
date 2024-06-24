import flask
import flask_login
import structlog
import pathlib

import click

from vancelle.clients.goodreads.csv import GoodreadsCsvImporter
from vancelle.clients.goodreads.html import GoodreadsHtmlImporter
from vancelle.ext.flask_login import get_user
from vancelle.extensions import db
from vancelle.shelf import Shelf


logger = structlog.get_logger(logger_name=__name__)

bp = flask.Blueprint("data", __name__)
bp.cli.short_help = "Import and export data."


@bp.record_once
def setup(state: flask.sansio.blueprints.BlueprintSetupState):
    state.app.config.setdefault(
        "GOODREADS_SHELF_MAPPING",
        {
            "currently-reading": Shelf.PLAYING,
            "gave-up-on": Shelf.ABANDONED,
            "read": Shelf.COMPLETED,
            "to-read": Shelf.UPCOMING,
            # Personal shelf names.
            "non-fiction": Shelf.PAUSED,
            "to-read-maybe": Shelf.UNDECIDED,
            "to-read-non-fiction": Shelf.SHELVED,
            "to-read-sequels": Shelf.UPCOMING,
        },
    )


@bp.before_request
@flask_login.login_required
def before_request():
    pass


@bp.cli.command("migrate")
def migrate():
    """Run temporary data migrations."""
    pass


@bp.cli.command("import-goodreads-csv")
@click.argument(
    "path",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path),
    default="goodreads_library_export.csv",
)
@click.option("--username", required=True)
def cli_import_csv(path: pathlib.Path, username: str) -> None:
    """
    Import from a goodreads_library_export.csv file.

    internetarchive/openlibrary skips books with no ISBN attached.

    https://github.com/internetarchive/openlibrary/blob/master/openlibrary/plugins/upstream/account.py#L1143
    """
    loader = GoodreadsCsvImporter(
        shelf_mapping=flask.current_app.config["GOODREADS_SHELF_MAPPING"],
        user=get_user(username),
    )
    for item in loader.load_file(path):
        db.session.add(item)
        db.session.commit()


@bp.cli.command("import-goodreads-html")
@click.argument("path", type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path))
@click.option("--username", required=True)
def cli_import_html(path: pathlib.Path, username: str) -> None:
    """Import books from manually scraped HTML."""
    loader = GoodreadsHtmlImporter(
        shelf_mapping=flask.current_app.config["GOODREADS_SHELF_MAPPING"],
        user=get_user(username),
    )
    for item in loader.load_file(path):
        db.session.add(item)
        db.session.commit()
