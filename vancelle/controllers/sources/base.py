import abc
import dataclasses
import typing

import flask
from flask_sqlalchemy.pagination import Pagination

from vancelle.models.remote import Remote

R = typing.TypeVar("R", bound=Remote, contravariant=True)


@dataclasses.dataclass()
class Manager(typing.Generic[R], abc.ABC):
    remote_type: typing.ClassVar[typing.Type[Remote]]

    def render_template(self, name: str, **context) -> str:
        identity = self.remote_type.identity()
        template_name = [f"remote/{identity}/{name}", f"remote/{name}"]
        return flask.render_template(template_name, **context, **self.context())

    def context(self) -> typing.Mapping[str, typing.Any]:
        return {"source": self.remote_type.info}

    def context_detail(self, remote: R) -> typing.Mapping[str, typing.Any]:
        return {}

    @abc.abstractmethod
    def fetch(self, remote_id: str) -> R:
        """
        Return a single Remote, fetched from an external source.

        May implement caching if desired.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def search(self, query: str) -> Pagination:
        """Return a flask_sqlalchemy.Pagination object containing Remotes."""
        raise NotImplementedError
