import abc
import dataclasses
import typing


from vancelle.lib.pagination import Pagination
from vancelle.models import Work
from vancelle.models.remote import Remote, RemoteInfo

R = typing.TypeVar("R", bound=Remote)


@dataclasses.dataclass()
class Source(typing.Generic[R], abc.ABC):
    """All sources have a remote type, but not all remote types have a source."""

    work_type: typing.ClassVar[typing.Type[Work]]
    remote_type: typing.ClassVar[typing.Type[Remote]]

    @abc.abstractmethod
    def fetch(self, remote_id: str) -> R:
        """
        Return a single Remote, fetched from an external source.

        May implement caching if desired.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def search(self, query: str) -> Pagination:
        """Return a Pagination object containing Remotes."""
        raise NotImplementedError

    @property
    def name(self) -> str:
        return self.remote_type.info.noun_full

    @property
    def info(self) -> RemoteInfo:
        return self.remote_type.info

    @classmethod
    def type(cls) -> str:
        return cls.remote_type.polymorphic_identity()

    def context(self, remote: R) -> typing.Mapping[str, typing.Any]:
        """Context for detail pages."""
        return {}

    @classmethod
    def subclasses(cls) -> typing.Sequence["Source"]:
        subclasses = (subclass() for subclass in cls.__subclasses__() if subclass.remote_type.info.is_external_source)
        return list(sorted(subclasses, key=lambda s: s.remote_type.info.noun_full))
