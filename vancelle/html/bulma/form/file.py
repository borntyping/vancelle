from vancelle.html.document import div, label, span
from vancelle.html.hotmetal import Hotmetal, element


def bulma_file_input(name: str) -> Hotmetal:
    return div(
        {"class": "file has-name is-fullwidth"},
        [
            label(
                {"class": "file-label"},
                [
                    element("input", {"class": "file-input", "type": "file", "name": name}, ()),
                    span({"class": "file-cta"}, [span({"class": "file-label"}, ["Choose a file..."])]),
                    span({"class": "file-name"}, ()),
                ],
            )
        ],
    )
