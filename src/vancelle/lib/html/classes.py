import typing

HtmlClasses = typing.Union[str, typing.Mapping[str, bool], typing.Iterable[str], None]


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
    Hotmetal implements something very similar in 'hotmetal.utils.classnames'.
    WTForms implements something very similar in 'wtforms.widgets.html_params'.
    """
    return " ".join(_html_classes_flatten(items))
