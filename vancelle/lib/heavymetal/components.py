"""
Functions and classes for building things heavymetal can render.
"""

import dataclasses
import time

import structlog

from .core import render
from .types import Heavymetal, HeavymetalProtocol

logger = structlog.get_logger(logger_name=__name__)


class HeavymetalComponent(HeavymetalProtocol):
    """Mixin for objects that can be rendered as with Heavymetal."""

    def heavymetal(self) -> Heavymetal:
        raise NotImplementedError

    def render(self) -> str:
        start = time.perf_counter_ns()
        tree = render(self)
        end = time.perf_counter_ns()
        logger.debug("Rendered component to HTML", type=type(self), duration=(end - start), seconds=(end - start) / 1000000000)
        return tree


@dataclasses.dataclass
class HeavymetalElement(HeavymetalComponent):
    """Sometimes mutability is nice."""

    tag: str
    attrs: dict[str, str | bool | None]
    children: list[Heavymetal]

    def heavymetal(self) -> Heavymetal:
        return (self.tag, self.attrs, self.children)
