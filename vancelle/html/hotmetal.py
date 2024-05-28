import dataclasses
import typing

import hotmetal
import structlog

logger = structlog.get_logger(logger_name=__name__)

HotmetalTag = str
HotmetalAttrs = dict[str, str]
HotmetalChildren = typing.Sequence["Hotmetal"]
HotmetalCallable = typing.Callable[[...], "Hotmetal"]
Hotmetal = HotmetalCallable | str | hotmetal.safe | typing.Tuple[HotmetalTag, HotmetalAttrs, HotmetalChildren]


ExtendedHotmetalAttrs = dict[str, str | bool]


class HotmetalClass(HotmetalCallable):
    def __call__(self, context: typing.Any) -> Hotmetal:
        raise NotImplementedError

    def render(self) -> str:
        return hotmetal.render(self)


@dataclasses.dataclass(slots=True)
class HotmetalElement(HotmetalClass):
    """
    A callable constructor for a Hotmetal tuple.

    This is used:
    - to make helper methods using `functools.partial(element, tag)`.
    - to provide type annotations where they might not already be present.
    - to inject debugging helpers, like raising an error on attrs with a None value.
    """

    tag: str
    attrs: HotmetalAttrs
    children: list[Hotmetal]

    def __init__(self, tag: HotmetalTag, attrs: ExtendedHotmetalAttrs, children: HotmetalChildren) -> None:
        self.tag = tag
        self.attrs = dict(self._process_attrs(attrs, tag=tag))
        self.children = list(children)

    def __call__(self, context: typing.Any) -> Hotmetal:
        return self.hotmetal

    @property
    def hotmetal(self) -> Hotmetal:
        return (self.tag, self.attrs, self.children)

    @staticmethod
    def _process_attrs(attrs: HotmetalAttrs, *, tag: str) -> typing.Iterable[typing.Tuple[str, str]]:
        for key, value in attrs.items():
            match key, value:
                case key, True:
                    yield key, ""
                case _, False:
                    continue
                case key, None:
                    continue
                case key, value:
                    yield key, value


def element(tag: HotmetalTag, attrs: HotmetalAttrs, children: HotmetalChildren) -> Hotmetal:
    return HotmetalElement(tag, attrs, children).hotmetal
