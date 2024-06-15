import typing

HeavymetalTag = str | None
HeavymetalAttrs = typing.Mapping[str, str | bool | None]
HeavymetalContent = typing.Sequence["Heavymetal"]
HeavymetalIterator = typing.Iterator["Heavymetal"]
HeavymetalCallable = typing.Callable[[], "Heavymetal"]
HeavymetalTuple = typing.Tuple[HeavymetalTag, HeavymetalAttrs, HeavymetalContent]
Heavymetal = HeavymetalCallable | str | HeavymetalTuple


@typing.runtime_checkable
class HeavymetalProtocol(typing.Protocol):
    def heavymetal(self) -> Heavymetal:
        ...
