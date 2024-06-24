import abc
import dataclasses
import typing


from vancelle.lib.pagination import Pagination
from vancelle.models import Work
from vancelle.models.entry import Entry, EntryInfo

E = typing.TypeVar("E", bound=Entry)


@dataclasses.dataclass()
class Source(typing.Generic[E], abc.ABC):
    """All sources have a remote type, but not all remote types have a source."""

    work_type: typing.ClassVar[typing.Type[Work]]
    entry_type: typing.ClassVar[typing.Type[Entry]]

    @abc.abstractmethod
    def fetch(self, entry_id: str) -> E:
        """
        Return a single Remote, fetched from an external source.

        May implement caching if desired.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def search(self, query: str) -> Pagination[Entry]:
        """Return a Pagination object containing Entries."""
        raise NotImplementedError

    @property
    def name(self) -> str:
        return self.entry_type.info.noun_full

    @property
    def info(self) -> EntryInfo:
        return self.entry_type.info

    @classmethod
    def polymorphic_identity(cls) -> str:
        return cls.entry_type.polymorphic_identity()

    def context(self, entry: E) -> typing.Mapping[str, typing.Any]:
        """Context for detail pages."""
        return {}

    @classmethod
    def subclasses(cls) -> typing.Sequence["Source"]:
        subclasses = (subclass() for subclass in cls.__subclasses__() if subclass.entry_type.info.is_external_source)
        return list(sorted(subclasses, key=lambda s: s.entry_type.info.noun_full))
