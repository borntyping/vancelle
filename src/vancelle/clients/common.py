import typing
import datetime

import structlog

logger = structlog.get_logger(logger_name=__name__)


def parse_date(string: str | None, formats: typing.Sequence[str]) -> datetime.date | None:
    if string is None:
        return None

    for fmt in formats:
        try:
            return datetime.datetime.strptime(string, fmt).date()
        except ValueError:
            pass

    return None
