from vancelle.html.helpers import merge_attrs
from vancelle.lib.heavymetal import Heavymetal, HeavymetalAttrs, HeavymetalDynamicContent
from vancelle.lib.heavymetal.html import div


def row(attrs: HeavymetalAttrs, content: HeavymetalDynamicContent) -> Heavymetal:
    return div(merge_attrs({"class": "row"}, attrs), content)


def col(attrs: HeavymetalAttrs, content: HeavymetalDynamicContent) -> Heavymetal:
    return div(merge_attrs({"class": "col"}, attrs), content)
