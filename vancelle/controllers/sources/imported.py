from werkzeug.exceptions import BadRequest

from .base import Manager
from ...ext.flask_sqlalchemy import Pagination
from ...models import ImportedWork


class ImportedWorkManager(Manager):
    remote_type = ImportedWork

    def fetch(self, remote_id: str) -> ImportedWork:
        raise BadRequest("Can't refresh imported data")

    def search(self, query: str) -> Pagination[ImportedWork]:
        raise BadRequest("Can't search imported data")
