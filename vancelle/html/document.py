import functools

import hotmetal

from .hotmetal import Hotmetal, element


def document(*children: Hotmetal) -> Hotmetal:
    doctype = hotmetal.safe("<!DOCTYPE html>")
    html = ("html", {"lang": "en"}, children)
    return ("", {}, [doctype, html])


def meta(name: str, content: str) -> Hotmetal:
    return element("meta", {"name": name, "content": str(content)}, ())


def link(rel: str, href: str, **attrs: str | None) -> Hotmetal:
    return element("link", {"rel": rel, "href": href, **attrs}, ())


def img(
    src: str,
    id: str | None = None,
    alt: str | None = None,
    width: str | int | None = None,
    height: str | int | None = None,
    style: str | None = None,
) -> Hotmetal:
    return element("img", {"id": id, "src": src, "alt": alt, "width": width, "height": height, "style": style}, ())


def script(src: str, crossorigin: str = "anonymous", type: str | None = None) -> Hotmetal:
    return element("script", {"src": src, "crossorigin": crossorigin, "type": type}, [])


def whitespace() -> str:
    return " "


a = functools.partial(element, "a")
button = functools.partial(element, "button")
code = functools.partial(element, "code")
div = functools.partial(element, "div")
form = functools.partial(element, "form")
h1 = functools.partial(element, "h1")
h2 = functools.partial(element, "h2")
header = functools.partial(element, "header")
label = functools.partial(element, "label")
p = functools.partial(element, "p")
section = functools.partial(element, "section")
span = functools.partial(element, "span")
