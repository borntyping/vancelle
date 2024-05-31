"""
Functions for building HTML elements.
"""

import typing

import markupsafe

from .types import HeavymetalAttrs, HeavymetalContent, HeavymetalTag, HeavymetalTuple


def fragment(children: HeavymetalContent) -> HeavymetalTuple:
    """
    Builds a Heavymetal tuple for a fragment.

    (i.e. a tuple that won't create a HTML element, but that can have children.)
    """
    return (None, {}, children)


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


def make_element(tag: str):
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
button = make_element("button")
code = make_element("code")
div = make_element("div")
footer = make_element("footer")
figure = make_element("figure")
form = make_element("form")
h1 = make_element("h1")
h2 = make_element("h2")
h3 = make_element("h3")
header = make_element("header")
label = make_element("label")
main = make_element("main")
nav = make_element("nav")
p = make_element("p")
picture = make_element("picture")
pre = make_element("pre")
section = make_element("section")
span = make_element("span")
title = make_element("title")
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