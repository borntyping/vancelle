import dataclasses
import typing

from vancelle.controllers.sources import EXTERNAL_SOURCES, Source


@dataclasses.dataclass(init=False)
class ExternalRemoteController:
    mapping: typing.Mapping[str, Source]

    def __init__(self) -> None:
        self.mapping = {source.remote_type.polymorphic_identity(): source for source in EXTERNAL_SOURCES}

    def __iter__(self) -> typing.Iterable[Source]:
        return self.mapping.values()

    def __getitem__(self, source_type: str) -> Source:
        return self.mapping[source_type]

    @property
    def sources(self) -> typing.Sequence[Source]:
        return list(sorted(self.mapping.values(), key=lambda source: source.name))
