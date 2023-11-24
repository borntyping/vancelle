from sqlalchemy import select

from vancelle.extensions import db
from vancelle.models import User


def get_user(username: str) -> User:
    """Get a user for use in CLI commands."""
    return db.session.execute(select(User).filter_by(username=username)).scalar_one()
