import typing

from .classes import html_classes

HtmlAttrs = typing.TypeVar("HtmlAttrs", bound=typing.Mapping[str, typing.Any])


def html_attrs(*items: HtmlAttrs) -> HtmlAttrs:
    """
    Merge HTML attribute dicts. The class= attribute gets special handling to
    merge classes.

    The type for HtmlAttrs is deliberately compatible with Heavymetal.
    """
    result: dict[str, typing.Any] = {}
    for attrs in items:
        for k, v in attrs.items():
            if k == "class":
                result[k] = html_classes(result.get(k, None), v)
                continue

            if k in result:
                raise ValueError(f"Duplicate attribute {k!r}")

            result[k] = v

    return result
