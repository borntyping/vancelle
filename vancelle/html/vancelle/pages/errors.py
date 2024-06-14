import flask

from vancelle.html.vancelle.components.header import page_header, section_header
from vancelle.html.vancelle.pages.base import page
from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import a, div, h1, h3, p, section


def error_page(title: str, description: str) -> Heavymetal:
    return page(
        [
            div(
                {"id": "error"},
                [
                    h1({"class": "display-3 text-danger"}, [title]),
                    p({"class": "lead"}, [description]),
                ],
            )
        ],
        title=["Error"],
    )


def debug_page():
    errors = [
        ("Exception", flask.url_for("errors.raise_generic_error")),
        ("vancelle.exceptions.ApplicationError", flask.url_for("errors.raise_application_error")),
        ("werkzeug.exceptions.HTTPException", flask.url_for("errors.raise_http_error")),
    ]

    return page(
        [
            page_header("Errors", "Trigger error messages for debugging"),
            section_header("Error pages"),
            p(
                {"class": "d-flex justify-content-start gap-2"},
                [a({"class": "btn btn-danger", "href": url}, [name]) for name, url in errors],
            ),
            section_header("HTMX error notifications"),
            p(
                {"class": "d-flex justify-content-start gap-2"},
                [a({"class": "btn btn-warning", "hx-get": url}, [name]) for name, url in errors],
            ),
        ],
        title=["Debug"],
    )
