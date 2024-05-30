import markupsafe
import pytest

from vancelle.lib.heavymetal import HeavymetalSyntaxError, render


def test_render():
    assert render(("span", {"title": "example"}, ["example"])) == '<span title="example">example</span>'


def test_render_void():
    assert render(("br", {}, [])) == "<br />"


def test_render_fragment():

    assert render((None, {}, [])) == ""
    assert render((None, {}, [("br", {}, [])])) == "<br />"


def test_render_doctype():
    document = (None, {}, [markupsafe.Markup("<!DOCTYPE html>"), ("html", {}, [])])
    assert render(document) == "<!DOCTYPE html><html />"


def test_passing_tuple_as_children():
    document = ("div", {}, ("div", {}, []))

    with pytest.raises(HeavymetalSyntaxError):
        assert render(document) == "<br />"
