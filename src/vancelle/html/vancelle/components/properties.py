import dataclasses
import typing

from vancelle.lib.heavymetal import Heavymetal, HeavymetalComponent
from vancelle.lib.heavymetal.html import abbr, table, tbody, td, th, tr
from vancelle.models.properties import Property


@dataclasses.dataclass()
class PropertiesTable(HeavymetalComponent):
    properties: typing.Sequence[Property]

    def __init__(self, properties: typing.Iterable[Property]) -> None:
        self.properties = tuple(properties)

    def heavymetal(self) -> Heavymetal:
        return table(
            {"class": "table"},
            [
                tbody(
                    {},
                    [
                        tr(
                            {},
                            [
                                th({"scope": "row"}, [abbr({"title": prop.title}, [prop.name])]),
                                td({}, [prop]),
                            ],
                        )
                        for prop in self.properties
                        if prop
                    ],
                )
            ],
        )
