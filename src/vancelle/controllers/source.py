import dataclasses
import typing

from vancelle.controllers.sources import Source


@dataclasses.dataclass(init=False)
class SourceController:
    mapping: typing.Mapping[str, Source]

    def __init__(self) -> None:
        self.mapping = {source.remote_type.polymorphic_identity(): source for source in Source.subclasses()}

    def __iter__(self) -> typing.Iterable[Source]:
        return self.mapping.values()

    def __getitem__(self, source_type: str) -> Source:
        return self.mapping[source_type]

    @property
    def sources(self) -> typing.Sequence[Source]:
        return list(self.mapping.values())
