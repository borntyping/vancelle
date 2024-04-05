import typing

from vancelle.html.hotmetal import HotmetalAttrs
from vancelle.inflect import p

HtmlClasses = str | typing.Mapping[str, bool] | typing.Iterable[str] | None


def _classnames_flatten(items: typing.Iterable[HtmlClasses]) -> typing.Iterable[str]:
    for item in items:
        if isinstance(item, str):
            yield item
        elif isinstance(item, typing.Mapping):
            yield from (k for k, v in item.items() if v)
        elif isinstance(item, typing.Iterable):
            yield from _classnames_flatten(item)
        elif item is None:
            pass
        else:
            raise TypeError(item)


def html_classes(*names: HtmlClasses) -> str:
    """
    Hotmetal implements something very similar in hotmetal.utils:classnames. This impl
    """
    return " ".join(_classnames_flatten(names))


def merge_attrs(a: HotmetalAttrs, b: HotmetalAttrs) -> HotmetalAttrs:
    merged = {"class": html_classes(a.get("class", None), b.get("class", None))}

    if duplicates := set(a.keys() - {"class"}) & set(b.keys() - {"class"}):
        raise Exception(f"Duplicate attributes: {p.join(list(duplicates))}")

    return a | b | merged
