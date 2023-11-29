import abc
import dataclasses
import typing

import flask_sqlalchemy.pagination

from vancelle.models import Work
from vancelle.models.remote import Remote

R = typing.TypeVar("R", bound=Remote)


@dataclasses.dataclass()
class Manager(typing.Generic[R], abc.ABC):
    remote_type: typing.ClassVar[typing.Type[Remote]]
    work_type: typing.ClassVar[typing.Type[Work]]

    @abc.abstractmethod
    def fetch(self, remote_id: str) -> R:
        """
        Return a single Remote, fetched from an external source.

        May implement caching if desired.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def search(self, query: str) -> flask_sqlalchemy.pagination.Pagination:
        """Return a flask_sqlalchemy.Pagination object containing Remotes."""
        raise NotImplementedError

    def context(self, remote: R) -> typing.Mapping[str, typing.Any]:
        """Context for detail pages."""
        return {}
