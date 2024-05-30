import typing

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


def count_plural(word: str, count: int) -> str:
    if not isinstance(count, int):
        raise ValueError("Count must be a number")

    return f"{count} {p.plural(word, count)}"
