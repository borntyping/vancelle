import flask

from vancelle.html.vancelle.pages.base import page
from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import a, div, h1, h3, p, section


def error_page(title: str, description: str) -> Heavymetal:
    return page(
        div(
            {"id": "error"},
            [
                h1({"class": "display-3 text-danger"}, [title]),
                p({"class": ""}, [description]),
            ],
        )
    )


def error_index_page():
    errors = [
        ("Exception", flask.url_for("errors.raise_generic_error")),
        ("vancelle.exceptions.ApplicationError", flask.url_for("errors.raise_application_error")),
        ("werkzeug.exceptions.HTTPException", flask.url_for("errors.raise_http_error")),
    ]

    return page(
        h1({"class": "display-3"}, "Errors"),
        p({}, "Trigger error messages for debugging"),
        h3({"class": "mt-5"}, "Error pages"),
        p(
            {"class": "d-flex justify-content-start gap-2"},
            [a({"class": "btn btn-danger", "href": url}, [name]) for name, url in errors],
        ),
        h3({"class": "mt-5"}, "HTMX error notifications"),
        p(
            {"class": "d-flex justify-content-start gap-2"},
            [a({"class": "btn btn-warning", "hx-get": url}, [name]) for name, url in errors],
        ),
    )
