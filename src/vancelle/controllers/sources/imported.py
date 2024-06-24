from werkzeug.exceptions import BadRequest

from .base import Source
from ...lib.pagination import Pagination
from ...models import Work
from ...models.entry import ImportedWork


class ImportedWorkSource(Source):
    entry_type = ImportedWork
    work_type = Work

    def fetch(self, entry_id: str) -> ImportedWork:
        raise BadRequest("Can't refresh imported data")

    def search(self, query: str) -> Pagination[ImportedWork]:
        raise BadRequest("Can't search imported data")
