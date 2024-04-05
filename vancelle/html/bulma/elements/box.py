import frozendict

from vancelle.html.document import div
from vancelle.html.helpers import merge_attrs
from vancelle.html.hotmetal import Hotmetal, HotmetalAttrs, HotmetalChildren


def box(*children: HotmetalChildren, attrs: HotmetalAttrs = frozendict.frozendict()) -> Hotmetal:
    return div(attrs=merge_attrs({"class": "box"}, attrs), children=children)
