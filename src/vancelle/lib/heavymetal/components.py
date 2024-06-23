"""
Functions and classes for building things heavymetal can render.
"""

import dataclasses

import sentry_sdk
import sentry_sdk.consts
import structlog

from .core import render
from .types import Heavymetal, HeavymetalProtocol, HeavymetalValue

logger = structlog.get_logger(logger_name=__name__)


class HeavymetalComponent(HeavymetalProtocol):
    """Mixin for objects that can be rendered as with Heavymetal."""

    def heavymetal(self) -> Heavymetal:
        raise NotImplementedError

    def render(self) -> str:
        with sentry_sdk.start_span(op=sentry_sdk.consts.OP.FUNCTION, description="HeavymetalComponent.render()") as span:
            span.set_tag("component", self.__class__.__qualname__)
            return render(self)


@dataclasses.dataclass
class HeavymetalMutableElement(HeavymetalComponent):
    """Sometimes mutability is nice."""

    tag: str
    attrs: dict[str, HeavymetalValue]
    children: list[Heavymetal]

    def heavymetal(self) -> Heavymetal:
        return (self.tag, self.attrs, self.children)
