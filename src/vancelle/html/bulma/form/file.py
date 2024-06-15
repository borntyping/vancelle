from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import div, input_, label, span


def bulma_file_input(name: str) -> Heavymetal:
    return div(
        {"class": "file has-name is-fullwidth"},
        [
            label(
                {"class": "file-label"},
                [
                    input_({"class": "file-input", "type": "file", "name": name}),
                    span({"class": "file-cta"}, [span({"class": "file-label"}, ["Choose a file..."])]),
                    span({"class": "file-name"}, ()),
                ],
            )
        ],
    )
