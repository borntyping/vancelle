import pathlib
import typing

import click
import flask
import flask_login

from .goodreads import bp as bp_goodreads
from .notion import bp as bp_notion
from ...controllers.data import DataController

controller = DataController()

bp = flask.Blueprint("data", __name__)
bp.cli.short_help = "Import and export data."

bp.register_blueprint(bp_goodreads)
bp.register_blueprint(bp_notion)


@bp.before_request
@flask_login.login_required
def before_request():
    pass


@bp.cli.command("export")
@click.argument(
    "file",
    type=click.File(mode="w", encoding="utf-8"),
    default=pathlib.Path("vancelle-backup.json"),
)
def cli_export_data(file: typing.TextIO) -> None:
    file.write(controller.export_json())


@bp.cli.command("import")
@click.argument(
    "file",
    type=click.File(mode="r", encoding="utf-8"),
    default=pathlib.Path("vancelle-backup.json"),
)
@click.option(
    "--dry-run/--no-dry-run",
    type=click.BOOL,
    default=False,
)
def cli_import_data(file: typing.TextIO, dry_run: bool) -> None:
    controller.import_json(json_data=file.read(), filename=file.name, dry_run=dry_run)
