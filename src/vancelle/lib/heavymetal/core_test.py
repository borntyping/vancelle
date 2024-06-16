import markupsafe
import pytest

from .types import Heavymetal, HeavymetalAnything, HeavymetalAttrs, HeavymetalProtocol
from .core import HeavymetalSyntaxError, render, attributes


class Example(HeavymetalProtocol):
    def heavymetal(self) -> Heavymetal:
        return ("div", {}, [])


@pytest.mark.parametrize(
    ("tree", "document"),
    [
        pytest.param(Example(), "<div></div>", id="protocol"),
        pytest.param(lambda: ("div", {}, []), "<div></div>", id="callable"),
        pytest.param(("span", {"title": "example"}, ["example"]), '<span title="example">example</span>', id="span"),
        pytest.param(("br", {}, []), "<br>", id="void"),
        pytest.param((None, {}, [("br", {}, [])]), "<br>", id="fragment"),
        pytest.param((None, {}, []), "", id="fragment-empty"),
        pytest.param(markupsafe.Markup("<!DOCTYPE html>"), "<!DOCTYPE html>", id="doctype"),
        pytest.param(
            (None, {}, [markupsafe.Markup("<!DOCTYPE html>"), ("html", {}, [])]),
            "<!DOCTYPE html><html></html>",
            id="html5",
        ),
    ],
)
def test_render(tree: HeavymetalAnything, document: str) -> None:
    assert render(tree) == document


@pytest.mark.parametrize(
    ("tree",),
    [
        pytest.param(("div", {}, ("div", {}, [])), id="tuple-as-children"),
    ],
)
def test_render_syntax_err(tree: HeavymetalAnything) -> None:
    with pytest.raises(HeavymetalSyntaxError):
        render(tree)


@pytest.mark.parametrize(
    ("attrs", "output"),
    [
        pytest.param({"key": "value"}, ' key="value"', id="True"),
        pytest.param({"disabled": True}, " disabled", id="True"),
        pytest.param({"disabled": False}, " ", id="False"),
        pytest.param({"disabled": None}, " ", id="None"),
    ],
)
def test_attributes(attrs: HeavymetalAttrs, output: str) -> None:
    assert attributes(attrs) == output
