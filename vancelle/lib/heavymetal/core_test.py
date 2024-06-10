import typing

import markupsafe
import pytest

from vancelle.lib.heavymetal import Heavymetal, HeavymetalProtocol, HeavymetalSyntaxError, render


class Example(HeavymetalProtocol):
    def heavymetal(self) -> Heavymetal:
        return ("div", {}, [])


@pytest.mark.parametrize(
    ("tree", "document"),
    [
        pytest.param(Example(), "<div></div>", id="protocol"),
        pytest.param(lambda: ("div", {}, []), "<div></div>", id="callable"),
        pytest.param(("span", {"title": "example"}, ["example"]), '<span title="example">example</span>', id="span"),
        pytest.param(("br", {}, []), "<br />", id="void"),
        pytest.param((None, {}, [("br", {}, [])]), "<br />", id="fragment"),
        pytest.param((None, {}, []), "", id="fragment-empty"),
        pytest.param(markupsafe.Markup("<!DOCTYPE html>"), "<!DOCTYPE html>", id="doctype"),
        pytest.param(
            (None, {}, [markupsafe.Markup("<!DOCTYPE html>"), ("html", {}, [])]),
            "<!DOCTYPE html><html></html>",
            id="html5",
        ),
    ],
)
def test_render(tree: typing.Any, document: str) -> None:
    assert render(tree) == document


@pytest.mark.parametrize(
    ("tree",),
    [
        pytest.param(("div", {}, ("div", {}, [])), id="tuple-as-children"),
    ],
)
def test_render_syntax_err(tree) -> None:
    with pytest.raises(HeavymetalSyntaxError):
        render(tree)
