import flask.testing

from vancelle.html.vancelle.pages.base import Page
from vancelle.lib.heavymetal import render


def test_page(app: flask.Flask):
    with app.test_request_context():
        assert render(Page([])).startswith("<!DOCTYPE html>")
