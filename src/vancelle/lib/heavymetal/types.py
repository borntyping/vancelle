import types
import typing


HeavymetalTag = typing.Union[str, None]
HeavymetalValue = typing.Union[str, bool, None]
HeavymetalAttrs = typing.Mapping[str, HeavymetalValue]

# Static types are used internally after a tree is 'unpacked' and no longer contains any callables.
_HeavymetalStaticContent = typing.Sequence["_HeavymetalStatic"]
_HeavymetalStaticTuple = typing.Tuple[HeavymetalTag, HeavymetalAttrs, _HeavymetalStaticContent]
_HeavymetalStatic = typing.Union[_HeavymetalStaticTuple, str, types.EllipsisType]

# Dynamic heavymetal can include callables that unpack to more heavymetal.
HeavymetalCallable = typing.Callable[[], "Heavymetal"]
HeavymetalContent = typing.Sequence["HeavymetalAnything"]
HeavymetalTuple = typing.Tuple[HeavymetalTag, HeavymetalAttrs, HeavymetalContent]

# A 'friendly' return type that can be used in most places, especially in return signatures.
# This doesn't include callables, as callables can't return another callable.
Heavymetal = typing.Union["HeavymetalTuple", str, types.EllipsisType]

# A less-friendly type that includes everything that can be rendered with Heavymetal,
# used in the signature for 'render()'.
HeavymetalAnything = typing.Union[Heavymetal, "HeavymetalProtocol", HeavymetalCallable]


@typing.runtime_checkable
class HeavymetalProtocol(typing.Protocol):
    def heavymetal(self) -> Heavymetal: ...
