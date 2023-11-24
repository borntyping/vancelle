import pathlib

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
    "path",
    type=click.Path(exists=False, file_okay=True, dir_okay=False, path_type=pathlib.Path),
    default=pathlib.Path("vancelle-backup.json"),
)
def cli_export_data(path: pathlib.Path) -> None:
    path.write_text(controller.export_json())


@bp.cli.command("import")
@click.argument(
    "path",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path),
    default=pathlib.Path("vancelle-backup.json"),
)
def cli_import_data(path: pathlib.Path) -> None:
    controller.import_json(json_data=path.read_text(), filename=path.name)
