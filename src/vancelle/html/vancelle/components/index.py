import flask
import wtforms

from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import a, button, div, fragment


def IndexFormControls(*, search: wtforms.Field) -> Heavymetal:
    return fragment([
        search.label(),
        div(
            {"class": "input-group"},
            [
                search(label=False, placeholder="Search"),
                a(
                    {"class": "btn btn-secondary", "href": flask.url_for(flask.request.endpoint)},
                    ["Clear"],
                ),
                button({"class": "btn btn-primary", "type": "submit"}, ["Search"]),
            ],
        ),
    ])
