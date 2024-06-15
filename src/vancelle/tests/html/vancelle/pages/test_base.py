import flask.testing

from vancelle.html.vancelle.pages.base import page
from vancelle.lib.heavymetal import render


def test_page(app: flask.Flask):
    with app.test_request_context():
        assert render(page([])).startswith("<!DOCTYPE html>")
