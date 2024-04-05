import dataclasses
import typing

import hotmetal

HtmlClasses = str | typing.Mapping[str, bool] | typing.Iterable[str] | None
HotmetalAttributes = dict[str, str]
HotmetalTuple = typing.Tuple[str, HotmetalAttributes, "Hotmetal"]
Hotmetal = HotmetalTuple | str | hotmetal.safe | typing.Callable[[...], "Hotmetal"]


@dataclasses.dataclass(slots=True)
class Element:
    tag: str
    attrs: HotmetalAttributes
    children: typing.List[Hotmetal]

    def __call__(self, context: typing.Any) -> Hotmetal:
        return (self.tag, self.attrs, self.children)
