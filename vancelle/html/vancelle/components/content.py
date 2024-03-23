import typing

from vancelle.html.types import Hotmetal


def page_content(*content: Hotmetal) -> Hotmetal:
    return ("main", {"class": "section"}, [("div", {"class": "container block"}, list(content))])
