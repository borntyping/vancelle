import functools
import typing

from vancelle.inflect import p

HtmlClasses = str | typing.Mapping[str, bool] | typing.Iterable[str] | None
HtmlAttrs = typing.Mapping[str, str | typing.Any]


def _html_classes_flatten(items: typing.Iterable[HtmlClasses]) -> typing.Iterable[str]:
    for item in items:
        if isinstance(item, str):
            yield item
        elif isinstance(item, typing.Mapping):
            yield from (k for k, v in item.items() if v)
        elif isinstance(item, typing.Iterable):
            yield from _html_classes_flatten(item)
        elif item is None:
            pass
        else:
            raise TypeError(item)


def html_classes(*items: HtmlClasses) -> str:
    """
    Hotmetal implements something very similar in hotmetal.utils:classnames. This impl
    """
    return " ".join(_html_classes_flatten(items))


def merge_attrs(*items: HtmlAttrs) -> HtmlAttrs:
    """
    Merge two HTML attribute dicts. The class= attribute gets special handling
    to merge classes. It'd be nice if duplicates of other attributes raised an
    error, but the last will win.

    The type for HtmlAttrs is deliberately compatible with Heavymetal.
    """
    dicts = [dict(attrs) for attrs in items]
    del items  # don't reuse the original mappings, which still have "class" keys.
    classes = [attrs.pop("class", None) for attrs in dicts]
    merged = {"class": html_classes(*classes)}
    result = functools.reduce(lambda x, y: {**x, **y}, dicts, merged)
    return result


def count_plural(word: str, count: int) -> str:
    if not isinstance(count, int):
        raise ValueError("Count must be a number")

    return f"{count} {p.plural(word, count)}"
