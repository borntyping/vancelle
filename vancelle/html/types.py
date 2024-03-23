import typing

import hotmetal
import starlette.datastructures

ClassNames = str | typing.Mapping[str, bool] | typing.Iterable[str] | None
HotmetalAttributes = dict[str, str]
HotmetalTuple = typing.Tuple[str, HotmetalAttributes, "Hotmetal"]
Hotmetal = HotmetalTuple | str | hotmetal.safe | typing.Callable[[...], "Hotmetal"]
Href = str | starlette.datastructures.URL
