import typing

HeavymetalTag = str | None
HeavymetalAttrs = typing.Mapping[str, str | bool | None]
HeavymetalChildren = typing.Sequence["Heavymetal"]
HeavymetalCallable = typing.Callable[[], "Heavymetal"]
HeavymetalTuple = typing.Tuple[HeavymetalTag, HeavymetalAttrs, HeavymetalChildren]
Heavymetal = HeavymetalCallable | str | HeavymetalTuple


@typing.runtime_checkable
class HeavymetalProtocol(typing.Protocol):
    def heavymetal(self) -> Heavymetal: ...
