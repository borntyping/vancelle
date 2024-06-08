"""
Functions for building HTML elements.
"""

import typing

import markupsafe

from .types import HeavymetalAttrs, HeavymetalContent, HeavymetalTag, HeavymetalTuple


def fragment(children: HeavymetalContent) -> HeavymetalTuple:
    """
    Builds a Heavymetal tuple for a fragment.

    (i.e. a tuple that won't create an HTML element, but that can have children.)

    >>> from . import render
    >>> render(fragment([span({}, ['example'])]))
    '<span>example</span>'
    """
    return (None, {}, children)


def nothing() -> HeavymetalTuple:
    """
    An empty fragment.

    >>> from . import render
    >>> example: str | None = None
    >>> render(span({}, example) if example else nothing())
    ''
    """
    return fragment(())


def element(tag: HeavymetalTag, attrs: HeavymetalAttrs, children: HeavymetalContent) -> HeavymetalTuple:
    """
    Builds a Heavymetal tuple for an HTML element.
    """
    return (tag, attrs, children)


def html5(attrs: HeavymetalAttrs, content: HeavymetalContent, *, lang: str = "en") -> HeavymetalTuple:
    """Creates a <html> element with a HTML5 DOCTYPE."""
    doctype = markupsafe.Markup("<!DOCTYPE html>\n")
    html = ("html", {"lang": lang} | attrs, content)
    return fragment([doctype, html])


def make_element(tag: str) -> typing.Callable[[HeavymetalAttrs, HeavymetalContent], HeavymetalTuple]:
    def __element__(attrs: HeavymetalAttrs, children: HeavymetalContent) -> HeavymetalTuple:
        return element(tag, attrs, children)

    __element__.__name__ = tag
    __element__.__qualname__ = f"make_element({tag!r})"
    return __element__


def make_void_element(tag: str) -> typing.Callable[[HeavymetalAttrs], HeavymetalTuple]:
    def __element__(attrs: HeavymetalAttrs) -> HeavymetalTuple:
        return element(tag, attrs, [])

    __element__.__name__ = tag
    __element__.__qualname__ = f"make_void_element({tag!r})"
    return __element__


a = make_element("a")
aside = make_element("aside")
button = make_element("button")
code = make_element("code")
div = make_element("div")
em = make_element("em")
figure = make_element("figure")
footer = make_element("footer")
form = make_element("form")
h1 = make_element("h1")
h2 = make_element("h2")
h3 = make_element("h3")
h4 = make_element("h4")
h5 = make_element("h5")
header = make_element("header")
label = make_element("label")
li = make_element("li")
main = make_element("main")
nav = make_element("nav")
ol = make_element("ol")
p = make_element("p")
picture = make_element("picture")
pre = make_element("pre")
section = make_element("section")
span = make_element("span")
strong = make_element("strong")
table = make_element("table")
tbody = make_element("tbody")
td = make_element("td")
th = make_element("th")
thead = make_element("thead")
title = make_element("title")
tr = make_element("tr")
ul = make_element("ul")

# https://html.spec.whatwg.org/#void-elements
area = make_void_element("area")
base = make_void_element("base")
br = make_void_element("br")
col = make_void_element("col")
embed = make_void_element("embed")
hr = make_void_element("hr")
img = make_void_element("img")
input_ = make_void_element("input")
link = make_void_element("link")
meta = make_void_element("meta")
source = make_void_element("source")
track = make_void_element("track")
wbr = make_void_element("wbr")


def script(attrs: HeavymetalAttrs, children: HeavymetalContent = ()) -> HeavymetalTuple:
    """Script gets a special case as it frequently has no children."""
    return ("script", attrs, children)
