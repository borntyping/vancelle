import typing

from vancelle.html.types import ClassNames


def _classnames_flatten(items: typing.Iterable[ClassNames]) -> typing.Iterable[str]:
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


def html_classes(*names: ClassNames) -> str:
    """
    Hotmetal implements something very similar in hotmetal.utils:classnames. This impl
    """
    return " ".join(_classnames_flatten(names))


def _attr_value(key: str, value: str) -> str:
    if isinstance(value, str):
        return value
    # elif isinstance(value, int):
    #     return str(value)

    raise TypeError(f"Attribute value can't be converted to a string: {key}={value!r}")


def filter_empty_attributes(attributes: dict[str, str | None]) -> dict[str, str]:
    return {k: _attr_value(k, v) for k, v in attributes.items() if v is not None}
