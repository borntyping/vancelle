import functools
import typing

import hotmetal

from .helpers import filter_empty_attributes
from .types import Hotmetal


def meta(name: str, content: str) -> Hotmetal:
    return ("meta", {"name": name, "content": str(content)}, ())


def title(*parts: str) -> Hotmetal:
    return ("title", {}, [" - ".join(["Vancelle", *parts])])


def link(rel: str, href: str, **attrs: str | None) -> Hotmetal:
    return ("link", filter_empty_attributes({"rel": rel, **attrs, "href": href}), ())


def document(*children: Hotmetal) -> Hotmetal:
    return ("", {}, [hotmetal.safe("<!DOCTYPE html>"), ("html", {"lang": "en"}, children)])


def img(
    src: str,
    id: str | None = None,
    alt: str | None = None,
    width: str | int | None = None,
    height: str | int | None = None,
    style: str | None = None,
) -> Hotmetal:
    attrs = filter_empty_attributes({"id": id, "src": src, "alt": alt, "width": width, "height": height, "style": style})
    return ("img", attrs, ())


def script(src: str, crossorigin: str = "anonymous", type: str | None = None) -> Hotmetal:
    return ("script", filter_empty_attributes({"src": src, "crossorigin": crossorigin, "type": type}), [])


def whitespace() -> str:
    return " "


def element(tag: str, attrs: typing.Mapping[str, str | None], children: typing.Iterable[Hotmetal]) -> Hotmetal:
    return (tag, filter_empty_attributes(attrs), list(children))


div = functools.partial(element, "div")
p = functools.partial(element, "p")
a = functools.partial(element, "a")
section = functools.partial(element, "section")
span = functools.partial(element, "span")
