import functools

from vancelle.lib.heavymetal.html import element

row = functools.partial(element, "div", {"class": "row"})
col = functools.partial(element, "div", {"class": "col"})
