import flask
import flask_login
import structlog
from sqlalchemy import select

from vancelle.blueprints.goodreads import bp as bp_goodreads
from vancelle.extensions import db
from vancelle.models import Work

logger = structlog.get_logger(logger_name=__name__)

bp = flask.Blueprint("data", __name__)
bp.cli.short_help = "Import and export data."

bp.register_blueprint(bp_goodreads)


@bp.before_request
@flask_login.login_required
def before_request():
    pass


@bp.cli.command("migrate")
def migrate():
    """Run temporary data migrations."""
    works = db.session.execute(select(Work).filter_by(shelf=None)).scalars().all()
    for work in works:
        work.shelf = work.resolve_details().shelf
    db.session.commit()
    logger.critical("Added shelf to works", count=len(works))
