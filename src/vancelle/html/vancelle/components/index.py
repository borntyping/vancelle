import flask
import wtforms

from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import a, button, div, fragment


def SearchFormControls(*, field: wtforms.Field, placeholder: str = "") -> Heavymetal:
    clear_url = flask.url_for(flask.request.endpoint, **flask.request.view_args)
    clear = a({"class": "btn btn-secondary", "href": clear_url}, ["Clear"])
    submit = button({"class": "btn btn-primary", "type": "submit"}, ["Search"])
    search = field(label=False, placeholder=placeholder)
    return fragment([field.label(), div({"class": "input-group"}, [search, clear, submit])])
