import csv
import datetime
import hashlib
import pathlib
import re
import typing
import uuid

import click
import flask
import structlog

from vancelle.extensions import db
from vancelle.models import User
from vancelle.models.remote import ImportedWork, Remote, SteamApplication
from vancelle.models.record import Record
from vancelle.models.work import Work
from vancelle.shelf import Shelf
from vancelle.ext.flask_login import get_user

steam_url_regex = re.compile(r"https://store\.steampowered\.com/app/(\d+)/.+/")

bp = flask.Blueprint("notion", __name__, url_prefix="/notion")
bp.cli.short_help = "Import from a CSV export of Sam's personal Notion database."

logger = structlog.get_logger(logger_name=__name__)

_unset = object()


@bp.cli.command("import")
@click.argument(
    "path",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path),
)
@click.option("--username", required=True)
def import_notion_csv(path: pathlib.Path, username: str):
    user = get_user(username)

    with path.open("r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    logger.info("Loaded CSV", count=len(rows))

    loader = NotionLoader()
    works = [loader.row(row, user=user, path=path) for row in rows]
    logger.info("Transformed rows", count=len(works))

    db.session.add_all(works)
    db.session.commit()
    logger.warning("Imported works from Notion", count=len(works))


class NotionLoader:
    date_formats: list[str] = ["%d/%m/%Y", "%d/%m/%Y %H:%M"]
    time_formats: list[str] = ["%B %d, %Y %I:%M %p"]

    work_types: dict[str, str] = {
        "Anime": "show",
        "Board game": "default",
        "Comicbook": "book",
        "Fiction (written unpublished)": "book",
        "Fiction (written)": "book",
        "Film": "film",
        "Music": "default",
        "Non-fiction (written)": "book",
        "Role playing games": "default",
        "Television (D&D)": "show",
        "Television (non-fiction)": "show",
        "Television": "show",
        "Video games": "game",
        "Webcomic": "default",
    }

    shelves_to_tags: dict[str, str] = {
        "Anime": {"anime"},
        "Board game": {"board-game"},
        "Comicbook": {"comic"},
        "Fiction (written unpublished)": {"unpublished"},
        "Fiction (written)": {},
        "Film": {},
        "Music": {"music"},
        "Non-fiction (written)": {"non-fiction"},
        "Role playing games": {"rpg"},
        "Television (D&D)": {"rpg"},
        "Television (non-fiction)": {"non-fiction"},
        "Television": {},
        "Video games": {},
        "Webcomic": {"webcomic"},
    }

    shelves: dict[str, Shelf] = {
        "Unreleased": Shelf.UNRELEASED,
        "Maybe next": Shelf.UNDECIDED,
        "Next": Shelf.UPCOMING,
        "Now playing": Shelf.PLAYING,
        "Online": Shelf.INFINITE,
        "Shelved": Shelf.PAUSED,
        "Done": Shelf.COMPLETED,
        "Done / Maybe": Shelf.SHELVED,
        "Done / Infinite": Shelf.COMPLETED,
        "Done / Not started": Shelf.ABANDONED,
        "Done / Not finished": Shelf.ABANDONED,
    }

    def _parse_time(self, value: str, formats: list[str]) -> datetime.datetime | None:
        if not value:
            return None

        for f in formats:
            try:
                return datetime.datetime.strptime(value, f)
            except ValueError:
                pass

        raise ValueError(f"Could not parse {value}")

    def parse_date(self, value: str) -> datetime.date | None:
        """
        >>> NotionLoader().parse_date('19/10/2023')
        datetime.date(2023, 10, 19)
        >>> NotionLoader().parse_date('02/02/2023 20:40')
        datetime.date(2023, 2, 2)
        """
        t = self._parse_time(value, self.date_formats)
        return t.date() if t is not None else None

    def parse_time(self, value: str) -> datetime.date | None:
        """
        >>> NotionLoader().parse_time("August 26, 2023 1:27 PM")
        datetime.datetime(2023, 8, 26, 13, 27)
        """
        return self._parse_time(value, self.time_formats)

    def parse_str(self, value: str, default: str | None = _unset) -> str | None:
        if not value:
            if default is not _unset:
                return default

            return None

        return value

    def row(self, row: dict[str, str], *, user: User, path: pathlib.Path) -> Work:
        try:
            id = uuid.UUID(hashlib.md5(str(row).encode("utf-8")).hexdigest())
            work = Work(
                id=id,
                user=user,
                type=self.work_types[row["Type"]],
                records=list(self.records(id=id, row=row)),
                remotes=list(self.remotes(id=id, row=row, path=path)),
            )
        except KeyError as e:
            logger.error("Missing key in row", key=e.args[0], row=row)
            raise

        return work

    def remotes(self, id: uuid.UUID, row: dict[str, str], path: pathlib.Path) -> typing.Iterable[Remote]:
        work_type = self.work_types[row["Type"]]
        time_created = self.parse_time(row["Created time"])
        time_updated = self.parse_time(row["Last edited time"])
        title = self.parse_str(row["Name"])
        release_date = self.parse_date(row["Release date"])
        shelf = self.shelves[row["Shelf"]]
        tags = self.shelves_to_tags.get(row["Shelf"], set())
        link = self.parse_str(row["Link"], None)

        if link and work_type == "game" and (match := steam_url_regex.match(link)):
            yield SteamApplication(id=match[1], data={"appid": match[1]})
            description = None
        else:
            description = link

        yield ImportedWork(
            id=id,
            time_created=time_created,
            time_updated=time_updated,
            title=title,
            description=description,
            release_date=release_date,
            shelf=shelf,
            tags=tags,
            data={"filename": path.name},
        )

    def records(self, id: uuid.UUID, row: dict[str, str]) -> typing.Iterable[Record]:
        date_started = self.parse_date(row["Started"])
        date_stopped = self.parse_date(row["Finished"])
        notes = self.parse_str(row["Bookmark"], None)

        if any((date_stopped, date_stopped, notes)):
            yield Record(id=id, date_started=date_started, date_stopped=date_stopped, notes=notes)
