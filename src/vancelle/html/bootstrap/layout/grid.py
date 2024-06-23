from vancelle.lib.html import html_attrs
from vancelle.lib.heavymetal import Heavymetal, HeavymetalAttrs, HeavymetalContent
from vancelle.lib.heavymetal.html import div


def row(attrs: HeavymetalAttrs, content: HeavymetalContent) -> Heavymetal:
    return div(html_attrs({"class": "row"}, attrs), content)


def col(attrs: HeavymetalAttrs, content: HeavymetalContent) -> Heavymetal:
    return div(html_attrs({"class": "col"}, attrs), content)
