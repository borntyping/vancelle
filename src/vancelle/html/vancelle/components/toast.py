import flask
import markupsafe

from vancelle.extensions import htmx
from vancelle.lib.html import HtmlClasses, html_classes
from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import aside, button, div, fragment, section, span, strong

TOAST_CONTAINER_ID = "v-notifications"


def toast(title: str, body: str, *, classes: HtmlClasses = ()) -> Heavymetal:
    return div(
        {"class": html_classes("toast show", classes)},
        [
            div(
                {"class": "toast-header"},
                [
                    strong({"class": "me-auto"}, [title]),
                    button({"class": "btn-close", "type": "button", "data-bs-dismiss": "toast"}, []),
                ],
            ),
            div({"class": "toast-body"}, [body]),
        ],
    )


def toast_response(title: str, body: str, *, classes: HtmlClasses = ()) -> Heavymetal:
    return fragment([
        span({}, [title, ": ", body]),
        section(
            {"id": TOAST_CONTAINER_ID, "hx-swap-oob": "beforeend"},
            [toast(title, body, classes=classes)],
        ),
    ])


def toast_container() -> Heavymetal:
    if htmx:
        toasts = []
    else:
        toasts = [
            toast(category, markupsafe.Markup(message))
            for category, message in flask.get_flashed_messages(with_categories=True)
        ]

    return aside(
        {
            "id": TOAST_CONTAINER_ID,
            "class": "toast-container position-fixed bottom-0 start-0 p-3",
            "style": "z-index: 11;",
            "hx-preserve": "true",
        },
        toasts,
    )
