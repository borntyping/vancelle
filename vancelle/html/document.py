import hotmetal

from .types import Hotmetal
from .helpers import filter_empty_attributes


def meta(name: str, content: str) -> Hotmetal:
    return ("meta", {"name": name, "content": str(content)}, ())


def title(*parts: str) -> Hotmetal:
    return ("title", {}, [" - ".join(["Vancelle", *parts])])


def link(rel: str, href: str, **attrs: str | None) -> Hotmetal:
    return ("link", filter_empty_attributes({"rel": rel, **attrs, "href": href}), ())


def document(*children: Hotmetal) -> Hotmetal:
    return ("", {}, [hotmetal.safe("<!DOCTYPE html>"), ("html", {"lang": "en"}, children)])


def a(
    *children: Hotmetal,
    href: str,
    id: str | None = None,
    title: str | None = None,
) -> Hotmetal:
    return ("a", filter_empty_attributes({"id": id, "href": href, "title": title}), list(children))


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
