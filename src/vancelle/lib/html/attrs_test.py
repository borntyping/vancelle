import typing

import pytest

from .attrs import html_attrs


def test_html_attrs_classes():
    assert html_attrs({"class": "row"}, {"class": "col"}) == {"class": "row col"}


def test_html_attrs_duplicate():
    with pytest.raises(ValueError, match="Duplicate attribute 'data-x'"):
        html_attrs({"data-x": "a"}, {"data-x": "b"})


def test_html_attrs_generic():
    import vancelle.lib.heavymetal

    a: vancelle.lib.heavymetal.HeavymetalAttrs = {"data-x": "a"}
    b: vancelle.lib.heavymetal.HeavymetalAttrs = {"data-y": "b"}
    c: vancelle.lib.heavymetal.HeavymetalAttrs = {"data-z": "c"}

    typing.assert_type(html_attrs(a, b, c), vancelle.lib.heavymetal.HeavymetalAttrs)
