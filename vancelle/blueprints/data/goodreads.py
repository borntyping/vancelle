import pathlib

import click
import flask

from vancelle.clients.goodreads.csv import GoodreadsCsvImporter
from vancelle.clients.goodreads.html import GoodreadsHtmlImporter
from vancelle.ext.flask_login import get_user
from vancelle.extensions import db
from vancelle.shelf import Shelf


bp = flask.Blueprint("goodreads", __name__)
bp.cli.short_help = "Import Goodreads CSV or HTML exports."


@bp.record_once
def setup(state: flask.sansio.blueprints.BlueprintSetupState):
    state.app.config.setdefault(
        "GOODREADS_SHELF_MAPPING",
        {
            "currently-reading": Shelf.PLAYING,
            "gave-up-on": Shelf.ABANDONED,
            "read": Shelf.COMPLETED,
            "to-read": Shelf.UNSORTED,
        },
    )


@bp.cli.command("import-csv")
@click.argument(
    "path",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path),
    default="goodreads_library_export.csv",
)
@click.option("--username", required=True)
def cli_import_csv(path: pathlib.Path, username: str) -> None:
    """
    Import books from goodreads_library_export.csv files.

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


@bp.cli.command("import-html")
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
